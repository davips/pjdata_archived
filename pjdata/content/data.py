from __future__ import annotations

from functools import lru_cache, cached_property
from typing import Tuple, Optional, TYPE_CHECKING, Iterator, Union, Literal, Dict

from pjdata.mixin.identification import WithIdentification

if TYPE_CHECKING:
    import pjdata.types as t
import pjdata.aux.compression as com
import pjdata.aux.uuid as u
import pjdata.mixin.linalghelper as li
import pjdata.transformer.transformer as tr
from pjdata.aux.util import Property
from pjdata.config import STORAGE_CONFIG


class Data(WithIdentification, li.LinAlgHelper):
    """Immutable lazy data for most machine learning scenarios.

    Parameters
    ----------
    history
        A tuple of Transformer objects.
    failure
        The reason why the workflow that generated this Data object failed.
    frozen
        Indicate wheter the workflow ended earlier due to a normal
        component behavior.
    hollow
        Indicate whether this is a Data object intended to be filled by
        Storage.
    storage_info
        An alias to a global Storage object for lazy matrix fetching.
    matrices
        A dictionary like {X: <numpy array>, Y: <numpy array>}.
        Matrix names should have a single uppercase character, e.g.:
        X=[
           [23.2, 35.3, 'white'],
           [87.0, 52.7, 'brown']
        ]
        Y=[
           'rabbit',
           'mouse'
        ]
        They can be, ideally, numpy arrays (e.g. storing is optimized).
        A matrix name followed by a 'd' indicates its description, e.g.:
        Xd=['weight', 'height', 'color']
        Yd=['class']
        A matrix name followed by a 't' indicates its types ('ord', 'int',
        'real', 'cat'*).
        * -> A cathegorical/nominal type is given as a list of nominal values:
        Xt=['real', 'real', ['white', 'brown']]
        Yt=[['rabbit', 'mouse']]
    """

    def __init__(
            self,
            history: Tuple[tr.Transformer, ...],
            failure: Optional[str],
            frozen: bool,
            hollow: bool,
            stream: Optional[Iterator[Data]],
            target: str = 's,r',  # Fields precedence when comparing which data is greater.
            storage_info: str = None,
            uuid: u.UUID = None,
            uuids: Dict[str, u.UUID] = None,
            **matrices,
    ):
        self._jsonable = matrices  # <-- TODO: put additional useful info
        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO:
        #  'name' and 'desc'
        #  volatile fields
        #  dna property?

        self.target = target.split(',')
        self.history = history
        self._failure = failure
        self._frozen = frozen
        self._hollow = hollow
        self.stream = stream
        self._target = [field for field in self.target if field.upper() in matrices]
        self.storage_info = storage_info
        self.matrices = matrices

        # Calculate UUIDs if not provided (this usually means this Data object is a newborn).
        if uuid:
            if uuids is None:
                raise Exception("Argument 'uuid' should be accompanied by a corresponding 'uuids'!")
            self._uuid, self.uuids = uuid, uuids
        else:
            self._uuid, self.uuids = li.evolve_id(u.UUID(), {}, history, matrices)

    def updated(self,
                transformers: Tuple[tr.Transformer, ...],
                failure: Optional[str] = 'keep',
                frozen: Union[bool, Literal['keep']] = 'keep',
                stream: Union[Iterator[Data], None, Literal["keep"]] = 'keep',
                **fields
                ) -> t.Data:
        """Recreate an updated Data object.

        Parameters
        ----------
        frozen
        transformers
            List of Transformer objects that transforms this Data object.
        failure
            Updated value for failure.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous
             failures
        fields
            Matrices or vector/scalar shortcuts to them.
        stream
            Iterator that generates Data objects.

        Returns
        -------
        New Content object (it keeps references to the old one for performance).
        """
        if failure == 'keep':
            failure = self.failure
        if frozen == 'keep':
            frozen = self.isfrozen
        if stream == 'keep':
            stream = self.stream
        matrices = self.matrices.copy()
        matrices.update(li.LinAlgHelper.fields2matrices(fields))

        uuid, uuids = li.evolve_id(self.uuid, self.uuids, transformers, matrices)

        return Data(
            # TODO: optimize history, nesting/tree may be a better choice, to build upon the ref to the previous history
            history=self.history + transformers,
            failure=failure, frozen=frozen, hollow=self.ishollow, stream=stream,
            storage_info=self.storage_info, uuid=uuid, uuids=uuids,
            **matrices
        )

    @Property
    def jsonable(self):
        return self._jsonable

    @cached_property
    def frozen(self):
        """TODO: Explicar aqui papéis de frozen...
            1- pipeline fim-precoce (p. ex. após SVM.enhance)
            2- pipeline falho (após exceção)
         """
        return Data(history=self.history,
                    failure=self.failure,
                    frozen=True,
                    hollow=self.ishollow,
                    stream=self.stream,
                    storage_info=self.storage_info,
                    **self.matrices)

    @cached_property
    def unfrozen(self):  # TODO: check if component Unfreeze is really needed
        return Data(history=self.history,
                    failure=self.failure,
                    frozen=False,
                    hollow=self.ishollow,
                    stream=self.stream,
                    storage_info=self.storage_info,
                    **self.matrices)

    @lru_cache()
    def hollow(self: t.Data, transformer: tr.Transformer):
        """Create a temporary hollow Data object (only Persistence can fill it).

        ps. History is not touched, only uuid."""
        uuid, uuids = li.evolve_id(self.uuid, self.uuids, (transformer,), self.matrices)
        return Data(history=self.history,
                    failure=self.failure,
                    frozen=self.isfrozen,
                    hollow=True,
                    stream=self.stream,
                    storage_info=self.storage_info,
                    uuid=uuid,
                    uuids=uuids,
                    **self.matrices)

    @lru_cache()
    def field(self, name, block=False, context: WithIdentification = "undefined"):
        """
        Safe access to a field, with a friendly error message.

        Parameters
        ----------
        name
            Name of the field.
        block
            Whether to wait for the value or to raise FieldNotReady exception if it is not readily available.
        context
            Scope hint about origin of the problem.

        Returns
        -------
        Matrix, vector or scalar
        """
        # TODO: better organize this code
        name = self._remove_unsafe_prefix(name, context)
        mname = name.upper() if len(name) == 1 else name

        # Check existence of the field.
        if mname not in self.matrices:
            comp = context.name if "name" in dir(context) else context
            raise MissingField(
                f"\n\nLast transformation:\n{self.history[-1]} ... \n"
                f" Data object <{self}>...\n"
                f"...last transformed by "
                f"{self.history[-1] and self.history[-1].name} does not "
                f"provide field {name} needed by {comp} .\n"
                f"Available matrices: {list(self.matrices.keys())}"
            )

        m = self.matrices[mname]

        # Fetch from storage?...
        if isinstance(m, u.UUID):
            if self.storage_info is None:
                comp = context.name if "name" in dir(context) else context
                raise Exception("Storage not set! Unable to fetch " + m.id, "requested by", comp)
            print(">>>> fetching field", name, m.id)
            self.matrices[mname] = m = self._fetch_matrix(m.id)

        # Fetch previously deferred value?...
        if callable(m):
            if block:
                raise NotImplementedError('Waiting of values not implemented yet!')
            self.matrices[mname] = m = m()

        # Just return formatted according to capitalization...
        if not name.islower():
            return m
        elif name in ["r", "s"]:
            return self._mat2sca(m)
        elif name in ["y", "z"]:
            return self._mat2vec(m)
        else:
            comp = context.name if "name" in dir(context) else context
            raise Exception("Unexpected lower letter:", m, "requested by", comp)

    def transformedby(self, transformer: tr.Transformer) -> t.Data:
        """Return this Data object transformed by func.

        Return itself if it is frozen or failed."""
        # ps. It is preferable to have this method in Data instead of Transformer because of the different handling
        # depending on the type of content: Data, NoData.
        if self.isfrozen or self.failure:
            return self  # TODO: updated((PHolder,)) ?
        result = transformer.rawtransform(self)
        if isinstance(result, dict):
            return self.updated(transformers=(transformer,), **result)
        return result

    @Property
    @lru_cache()
    def Xy(self):
        return self.field("X"), self.field("y")

    @Property
    def allfrozen(self):
        return False

    @Property
    @lru_cache()
    def matrix_names(self):
        return list(self.matrices.keys())

    @Property
    @lru_cache()
    def ids_lst(self):
        return [self.uuids[name].id for name in self.matrix_names]

    @Property
    @lru_cache()
    def ids_str(self):
        return ",".join(self.ids_lst)

    @Property
    @lru_cache()
    def history_str(self):
        return ",".join(transf.uuid.id for transf in self.history)

    @lru_cache()
    def field_dump(self, name):
        """Lazily compressed matrix for a given field.
        Useful for optimized persistence backends for Cache."""
        return com.pack(self.field(name))

    @Property
    @lru_cache()
    def matrix_names_str(self):
        return ",".join(self.matrix_names)

    @Property
    def isfrozen(self):
        return self._frozen

    @Property
    def ishollow(self):
        return self._hollow

    @lru_cache()
    def _fetch_matrix(self, id):
        if self.storage_info is None:
            raise Exception(f"There is no storage set to fetch {id})!")
        return STORAGE_CONFIG["storages"][self.storage_info].fetch_matrix(id)

    def _remove_unsafe_prefix(self, item, component="undefined"):
        """Handle unsafe (i.e. frozen) fields."""
        if item.startswith("unsafe"):
            # User knows what they are doing.
            return item[6:]

        if self.failure or self.isfrozen or self.ishollow:
            raise Exception(
                f"Component {component} cannot access fields ({item}) from Data objects that come from a "
                f"failed/frozen/hollow pipeline! HINT: use unsafe{item}. \n"
                f"HINT2: probably the model/enhance flags are not being used properly around a Predictor.\n"
                f"HINT3: To calculate training accuracy the 'train' Data should be inside the 'test' tuple; use Copy "
                f"for that."
            )  # TODO: breakdown this msg for each case.
        return item

    def _uuid_impl(self):
        return self._uuid

    @Property
    def failure(self) -> Optional[str]:
        return self._failure

    def __getattr__(self, item):
        """Create shortcuts to fields, still passing through sanity check."""
        if item == "Xy":
            return self.Xy
        if 0 < (len(item) < 3 or item.startswith("unsafe")):
            return self.field(item, "[direct access through shortcut]")

        # print('getting attribute...', item)
        return super().__getattribute__(item)

    def __lt__(self, other):
        """Amenity to ease pipeline result comparisons. 'A > B' means A is better than B."""
        for name in self._target:
            return self.field(name) < other.field(name, context='comparison between Data objects')
        return Exception("Impossible to make comparisons. None of the target fields are available:", self.target)

    def _name_impl(self):
        # return self._name
        raise NotImplementedError("We need to decide if Data has a name")  # <-- TODO

    def __eq__(self, other: t.Data) -> bool:
        # Checks removed for speed (isinstance is said to be slow...)
        # from pjdata.content.specialdata import NoData
        # if other is not NoData or not isinstance(other, Data):  # TODO: <-- check for other types of Data?
        #     return False
        return self.uuid == other.uuid

    def __hash__(self) -> int:
        return hash(self.uuid)


class MissingField(Exception):
    pass
