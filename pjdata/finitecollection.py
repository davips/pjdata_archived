from pjdata.collection import Collection


class FiniteCollection(Collection):
    from pjdata.specialdata import NoData

    def __init__(self, datas, history=None, failure=None, original_data=NoData,
                 uuid=None):
        super().__init__(history, failure, original_data, uuid)
        self._datas = datas
        self.size = len(datas)
        self.has_nones = not all(datas)

    def last_transformation_replaced(self, transformation):
        """Replace last transformation in history for convenience.

        Provided transformation should be equivalent to the replaced one for
        consistency.
        """
        return FiniteCollection(
            self._datas,
            history=self.history[:-1] + [transformation],
            failure=self.failure,
            original_data=self.original_data,
            uuid=self.uuid00 - self.history[-1].uuid00 + transformation.uuid00
        )

    def __str__(self):
        return 'FiniteCollection [' + \
               '\n'.join(str(data) for data in self._datas) + ']'
