from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np

from pjdata.abc.abstractdata import AbstractData
from pjdata.aux.compression import pack
from pjdata.aux.encoders import UUID
from pjdata.mixin.linalghelper import LinAlgHelper
from pjdata.mixin.printable import Printable


def evolve(uuid, transformations):
    for transformation in transformations:
        print(uuid, 'evolving through', transformation.name, transformation.uuid00)
        uuid += transformation.uuid00
        print('results in ', uuid)
    return uuid


def data(**matrices):  # new()?
    # Intended for Data and matrices created directly by the user.
    # self.history = []
    # self._uuid = UUID()
    #
    # # Calculate unique hash for the matrices.
    # packs = ''.encode()
    # for mat in matrices:
    #     packs += pack_data(mat)  # TODO: store uuids for each matrix
    # matrices_hexhash = hexuuid(packs)
    # matrices_hash = tiny_md5(matrices_hexhash)
    #
    # if 'nam-e' in matrices:
    #     matrices['name'] += '_' + matrices_hash[:6]
    #
    # class New:
    #     """Fake New transformer."""
    #     name = 'New'
    #     path = 'pjml.tool.data.flow.new'
    #     uuid = matrices_hash
    #     hexuuid = matrices_hexhash
    #     config = matrices
    #     jsonable = {'_id': f'{name}@{path}', 'config': config}
    #     serialized = serialize(jsonable)
    #
    # transformer = New()
    # # New transformations are always represented as 'u', no matter
    # # which step.
    # transformation = Transformation(transformer, 'u')
    # history = [transformation]

    # return Data()
    pass


class Data(AbstractData, LinAlgHelper, Printable):
    """Immutable data for all machine learning scenarios one can imagine.

    Attributes
    ----------
    matrices
        A dictionary, like {X: <numpy array>, Y: <numpy array>}.
        Matrix names should start with an uppercase letter and
        have at most two letters.
    fields
        Shorcuts 'matrices', but seeing each column-vector matrix as a vector
        and each single element matrix as a scalar.

    Parameters
    ----------
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

    # Some mappings from vector/scalar to the matrix where it is stored.
    _vec2mat_map = {i: i.upper() for i in ['y', 'z', 'v', 'w']}
    _sca2mat_map = {i: i.upper() for i in ['r', 's', 't']}

    def __init__(self, uuid, uuids, history, failure, storage=None,
                 **matrices):
        kwargs = matrices
        super().__init__(jsonable=kwargs)
        # TODO: Check if types (e.g. Mt) are compatible with values (e.g. M).

        # Separate matrices from the rest of kwargs ('name', 'desc' etc.).
        # TODO: what to do with info? 'name' and 'desc'?
        matrices = {}
        info = {}
        for k, v in kwargs.items():
            if len(k) < 3:
                matrices[k] = v
            else:
                info[k] = v

        self.history = history
        self._uuid = uuid
        self.uuids = uuids
        self.failure = failure
        self.storage = storage
        self.matrices = matrices
        self._fields = matrices.copy()

        # Add vector shortcuts.
        for k, v in self._vec2mat_map.items():
            if v in matrices and (
                    matrices[v].shape[0] == 1 or matrices[v].shape[1] == 1):
                self._fields[k] = self._matrix_to_vector(matrices[v])

        # Add scalar shortcuts.
        for k, v in self._sca2mat_map.items():
            if v in matrices and matrices[v].shape == (1, 1):
                self._fields[k] = self._matrix_to_scalar(matrices[v])

        self.__dict__.update(self._fields)

    def updated(self, transformations, failure='keep', **fields):
        """Recreate Data object with updated matrices, history and failure.

        Parameters
        ----------
        frozen
        transformations
            List of Transformation objects.
        failure
            The failure caused by the given transformation, if it failed.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous failures
        fields
            Changed/added matrices and updated values.

        dataset
            Original dataset where data was extract from.
        history
            History object of transformations.
        failure
            The cause, when the provided history leads to a failure.

        Returns
        -------
        New Data object (it keeps references to the old one for performance).
        """
        from pjdata.specialdata import NoData
        if failure == 'keep':
            failure = self.failure

        # Translate shortcuts.
        matrices = self.matrices.copy()
        for name, value in fields.items():
            new_name, new_value = Data._translate(name, value)
            matrices[new_name] = new_value

        uuid, uuids = self._evolve(transformations, matrices, fields)

        klass = Data if self is NoData else self.__class__
        return klass(
            uuid=uuid, uuids=uuids, history=self.history + transformations,
            failure=failure, **matrices
        )

    def field(self, name, component=None):
        if name not in self._fields:
            name = component.name if 'name' in dir(component) else component
            raise MissingField(
                f'\n=================================================\n'
                f'Last transformation:\n{self.history.last} ... \n'
                f' Data object <{self}>\n'
                f' last transformed by '
                f'{self.history.last and self.history.last.name} does '
                f'not provide field\n {name} needed by {name} .\n'
                f'Available fields: {list(self._fields.keys())}')
        return self._fields[name]

    @property
    @lru_cache()
    def Xy(self):
        return self.field('X'), self.field('y')

    @property
    @lru_cache()
    def field_names(self):
        return list(self._fields.keys())

    @property
    @lru_cache()
    def matrix_names(self):
        return list(self.matrices.keys())

    @property
    @lru_cache()
    def matrix_names_str(self):
        return ','.join(self.matrix_names)

    @property
    @lru_cache()
    def field_names_str(self):
        return ','.join(self.field_names)

    @property
    @lru_cache()
    def uuids_str(self):
        return ','.join(u.pretty for u in self.uuids.values())

    @property
    @lru_cache()
    def history_str(self):
        return ','.join(transf.uuid00.pretty for transf in self.history)

    @lru_cache()
    def field_dump(self, name):
        """Lazily compressed matrix for a given field.
        Useful for optimized persistence backends for Cache."""
        return pack(self.field(name))

    @property
    @lru_cache()
    def frozen(self):
        from pjdata.specialdata import FrozenData
        return FrozenData(self)

    @property
    def allfrozen(self):
        return False

    def mockup(self, transformations):
        """A tentative Data object, i.e. with a history ahead of its matrices.
        Usefull to anticipate the outcome (uuid/uuids) of a Pipeline
         (e.g. to allow Cache fetching)."""
        from pjdata.specialdata import MockupData

        # TODO: see TODO in init
        # if 'name' in self.matrices:
        #     kwargs['name'] = self.name
        # if 'desc' in self.matrices:
        #     kwargs['desc'] = self.desc

        new_uuid, new_uuids = self._evolve(transformations)
        return MockupData(uuid=new_uuid, uuids=new_uuids,
                          history=self.history + transformations,
                          failure=self.failure, **self.matrices)

    def _uuid_impl00(self):
        return self._uuid

    @classmethod
    def _translate(cls, field_name, value):
        """Given a field name, return its underlying matrix name and content.
        """
        if field_name in cls._vec2mat_map:
            # Vector.
            return field_name.upper(), cls._as_column_vector(value)
        elif field_name in cls._sca2mat_map:
            # Scalar.
            return field_name.upper(), np.array(value, ndmin=2)
        else:
            # Matrix given directly.
            return field_name, value

    def __getattr__(self, item):
        """Intercept any call to matrices to fetch them if needed."""
        if len(item) > 2:
            return super().__getattribute__(item)
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            if self.storage is None:
                raise MissingField(f'Field {item} not found!')
            return self.fetch_matrix(item)

    @lru_cache()
    def fetch_matrix(self, name):
        if self.storage is None:
            raise Exception(f'There is no storage set to fetch {name})!')
        return self.storage.fetch_matrix(self.field(name))

    def _evolve(self, transformations, new_matrices=None, fields=None):
        if new_matrices is None:
            new_matrices = self.matrices
        if fields is None:
            fields = self.matrices

        # Update UUID digests.
        uuids = {}
        for matrix_name in new_matrices:
            # If it is a new matrix, assign '0000000000000000000'.
            muuid = self.uuids.get(matrix_name, UUID())

            # Transform new fields' UUID.
            if matrix_name in fields:
                muuid = evolve(muuid, transformations)
            uuids[matrix_name] = muuid

        # Update UUID.
        uuid = evolve(self.uuid00, transformations)

        return uuid, uuids


class MissingField(Exception):
    pass
