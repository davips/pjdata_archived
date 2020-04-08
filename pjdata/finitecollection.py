from pjdata.collection import Collection
from pjdata.history import History


class FiniteCollection(Collection):
    from pjdata.data import NoData

    def __init__(self, datas, history=None, failure=None, original_data=NoData):
        super().__init__(history, failure, original_data)

        self._datas = datas
        self.size = len(datas)
        self.has_nones = not all(datas)

        self._uuids = ""
        for data in self._datas:
            self._uuids += data.uuid if data else "00000000000000000000"

    def updated(self, transformations, datas=None, failure='keep'):
        """Recreate Collection object with updated history, failure and datas.

        Parameters
        ----------
        transformations
            List of Transformation objects.
        failure
            The failure caused by the given transformation, if it failed.
            'keep' (recommended, default) = 'keep this attribute unchanged'.
            None (unusual) = 'no failure', possibly overriding previous failures
        datas
            New list of Data object.

        Returns
        -------
        New Collection object (it may keep some references for performance).
        """
        if failure == 'keep':
            failure = self.failure

        if datas is None:
            datas = self._datas

        # TODO: to require changes on Xt and Xd when X is changed.
        return FiniteCollection(
            datas=datas,
            history=self.history.extended(transformations),
            failure=failure,
            original_data=self.original_data
        )

    def last_transformation_replaced(self, transformation):
        """Replace last transformation in history for convenience.

        Provided transformation should be equivalent to the replaced one for
        consistency.
        """
        return FiniteCollection(
            self._datas,
            history=History(self.history[:-1] + [transformation]),
            failure=self.failure,
            original_data=self.original_data
        )

    def __str__(self):
        return '\n'.join(str(data) for data in self._datas)
