from functools import lru_cache

from pjdata.aux.decorator import classproperty
from pjdata.aux.serialization import serialize
from pjdata.aux.util import Property
from pjdata.aux.uuid import UUID
from pjdata.content.specialdata import NoData
from pjdata.mixin.serialization import withSerialization


class FakeFile(withSerialization):
    path = "pjml.tool.data.flow.file"

    def __init__(self, filename, original_hashes):
        clean = filename.replace(".ARFF", "").replace(".arff", "")
        split = clean.split("/")
        self.config = {
            "name": filename.split("/")[-1],
            "path": "/".join(split[:-1]) + "/",
            "hashes": original_hashes,
        }
        self.info_for_transformer = {"id": f"{self.name}@{self.path}", "config": self.config}
        self.jsonable = {"info": self.info_for_transformer, "enhance": True, "model": True}
        self.hasenhancer, self.hasmodel = True, True

    @Property
    @lru_cache()
    def cfserialized(self):
        return serialize(self.info_for_transformer)

    def _cfuuid_impl(self, data=None):
        return UUID(serialize(self.config["hashes"]).encode())

    def _name_impl(self):
        return "File"

    def _uuid_impl(self):
        return UUID(self.serialized.encode())
