from pjdata.collection import Collection


class FiniteCollection(Collection):
    from pjdata.specialdata import NoData

    def __init__(self, datas, history=None, failure=None, original_data=NoData,
                 uuid=None):
        super().__init__(history, failure, original_data, uuid)
        self._datas = datas
        self.size = len(datas)
        self.has_nones = not all(datas)

    def last_transformations_replaced(self, drop, transformation):
        """Replace last transformation in history for convenience.

        Provided transformation should be equivalent to the replaced one for
        consistency.
        """

        # Undo dropped transformations.
        history = self.history[:-drop]
        uuid = self.uuid
        for transformation_to_discard in reversed(self.history[-drop:]):
            uuid /= transformation_to_discard.uuid

        return FiniteCollection(
            self._datas,
            history=history + [transformation],
            failure=self.failure,
            original_data=self.original_data,
            uuid=uuid * transformation.uuid
        )

    def __str__(self):
        return 'FiniteCollection [' + \
               '\n'.join(str(data) for data in self._datas) + ']'
