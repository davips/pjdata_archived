from __future__ import annotations

from functools import lru_cache
from typing import Tuple, Optional

import typing

if typing.TYPE_CHECKING:
    import pjdata.types as t
import pjdata.aux.compression as com
import pjdata.aux.uuid as u
import pjdata.content.content as co
import pjdata.mixin.linalghelper as li
import pjdata.transformer as tr
from pjdata.aux.util import Property
from pjdata.config import STORAGE_CONFIG


class Data(li.LinAlgHelper, co.Content):
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
        storage_info: Optional[str] = None,
        **matrices,
    ):
        self._jsonable = matrices  # <-- TODO: put additional useful info
        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).
        # TODO:
        #  'name' and 'desc'
        #  volatile fields
        #  dna property?

        self.history = history
        self._failure = failure
        self._frozen = frozen
        self._hollow = hollow
        self.storage_info = storage_info
        self.matrices = matrices

        # Calculate UUIDs.
        self._uuid, self.uuids = self._evolve_id(u.UUID(), {}, history, matrices)

    @Property
    def jsonable(self):
        return self._jsonable

    @Property
    @lru_cache()
    def frozen(self):
        """frozen faz dois papéis:
            1- pipeline precoce (p. ex. após SVM.enhance)
            2- pipeline falho (após exceção)
        um terceiro papel não pode ser feito por ele, pois frozen é uma
        propriedade armazenável de Data:
            3- hollow = mockup p/ ser preenchido pelo cururu
         """
        return self.updated(transformers=tuple(), frozen=True)

    @lru_cache()
    def hollow(self: t.Data, transformations):
        """temporary hollow (only Persistence can fill it)         """
        return self.updated(transformers=transformations, hollow=True)

    @lru_cache()
    def field(self, name, component="undefined"):
        """Safe access to a field, with a friendly error message."""
        name = self._remove_unsafe_prefix(name, component)
        mname = name.upper() if len(name) == 1 else name

        # Check existence of the field.
        if mname not in self.matrices:
            comp = component.name if "name" in dir(component) else component
            raise MissingField(
                f"\n\nLast transformation:\n{self.history[-1]} ... \n"
                f" Data object <{self}>...\n"
                f"...last transformed by "
                f"{self.history[-1] and self.history[-1].name} does not "
                f"provide field {name} needed by {comp} .\n"
                f"Available matrices: {list(self.matrices.keys())}"
            )

        m = self.matrices[mname]

        # Fetch from storage if needed.
        if isinstance(m, u.UUID):
            if self.storage_info is None:
                raise Exception("Storage not set! Unable to fetch " + m.id)
            print(">>>> fetching field", name, m.id)
            self.matrices[mname] = m = self._fetch_matrix(m.id)

        if not name.islower():
            return m

        if name in ["r", "s"]:
            return self._mat2sca(m)

        if name in ["y", "z"]:
            return self._mat2vec(m)

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
                f"Component {component} cannot access fields from Data objects that come from a "
                f"failed/frozen/hollow pipeline! HINT: use unsafe{item}. \n"
                f"HINT2: probably an ApplyUsing is missing, around a Predictor."
            )
        return item

    def _uuid_impl(self):
        return self._uuid

    @property
    def failure(self) -> Optional[str]:
        return self._failure

    def __getattr__(self, item):
        """Create shortcuts to fields, still passing through sanity check."""
        if item == "Xy":
            return self.Xy
        if 0 < (len(item) < 3 or item.startswith("unsafe")):
            return self.field(item, "[direct access through shortcut]")

        # print('just curious...', item)
        return super().__getattribute__(item)

    # It does not work because of __hash__
    # def __eq__(self, other):
    #     """Overrides the default implementation"""
    #     if isinstance(other, Data):
    #         return self.uuid00 == other.uuid00
    #     return False

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __hash__(self):
        return hash(self.uuid)


class MissingField(Exception):
    pass
