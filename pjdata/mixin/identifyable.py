""" Identifyable Module. """
from abc import ABC, abstractmethod
from functools import lru_cache


class Identifyable(ABC):
    """ Identifyable mixin. """

    @property  # type: ignore
    @lru_cache()
    def uuid(self):
        """Lazily calculated unique identifier for this dataset.

        Should be accessed direct as a class member: 'uuid'.

        Returns
        -------
            A unique identifier UUID object.
        """
        # pylint: disable=import-outside-toplevel
        from pjdata.aux.uuid import UUID

        content = self._uuid_impl()
        if isinstance(content, UUID):
            return content
        return UUID(content.encode())

    @property  # type: ignore
    @lru_cache()
    def id(self):
        """
        Short uuID
        First 8 chars of uuid, usually for printing purposes.
        First collision expect after 12671943 combinations.
        :return:
        """
        return self.uuid.id

    @property  # type: ignore
    @lru_cache()
    def sid(self):
        """
        Short uuID
        First 6 chars of uuid, usually for printing purposes.
        :return:
        """
        return self.id[:6]

    @abstractmethod
    def _uuid_impl(self):
        """Specific internal calculation made by each child class.

        Should return a string or a UUID object to be used directly."""
