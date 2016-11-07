from datetime import datetime

from testtools.testresult.real import (
    INTERIM_STATES,
    utc,
    _TestRecord,
    _StreamToTestRecord,
)


class TestRecord(_TestRecord):

    @classmethod
    def create(cls, test_id, timestamp=None, status="unknown"):
        return cls(
            id=test_id,
            tags=set(),
            details={},
            status=status,
            timestamps=(timestamp or datetime.now(utc), None),
        )


class AsyncStreamToTestRecord(_StreamToTestRecord):

    def status(self, test_id=None, test_status=None, test_tags=None,
               runnable=True, file_name=None, file_bytes=None, eof=False,
               mime_type=None, route_code=None, timestamp=None):

        # XXX testtools doesn't take the eof field into account, since it
        #     accumulates all details received during INTERIM_STATES, firing
        #     them at the end. However we want to flush details as soon as they
        #     are available, so we mark the record with the eof field.
        key = self._ensure_key(test_id, route_code, timestamp)
        if key:
            record = self._inprogress[key]
            record.last_file_name = file_name
            record.eof = eof

        super(AsyncStreamToTestRecord, self).status(
            test_id, test_status,
            test_tags=test_tags, runnable=runnable, file_name=file_name,
            file_bytes=file_bytes, eof=eof, mime_type=mime_type,
            route_code=route_code, timestamp=timestamp)

        if key and test_status in INTERIM_STATES:
            self.on_test(record)
