from datetime import datetime

from testtools.testresult.real import (
    INTERIM_STATES,
    utc,
    _TestRecord,
    _StreamToTestRecord,
)


class TestRecord(_TestRecord):
    """A _TestRecord with a more convenient create() class method."""

    @classmethod
    def create(cls, test_id, timestamp=None, status="unknown", runnable=True):
        record = cls(
            id=test_id,
            tags=set(),
            details={},
            status=status,
            timestamps=(timestamp or datetime.now(utc), None),
        )
        record.runnable = runnable
        return record


class InterimStreamToTestRecord(_StreamToTestRecord):
    """
    Specialized _StreamToTestRecord that fires the on_test callback also upon
    interim states.
    """

    def status(self, test_id=None, test_status=None, test_tags=None,
               runnable=True, file_name=None, file_bytes=None, eof=False,
               mime_type=None, route_code=None, timestamp=None):

        # XXX testtools accumulates all details received during INTERIM_STATES,
        #     firing the 'got_case' callback only for non-interim states. Since
        #     we want to watch for log entries in real time, we need to also
        #     call back on interim states.
        key = self._ensure_key(test_id, route_code, timestamp)
        if key:
            record = self._inprogress[key]
            record.set(runnable=runnable)

        super(InterimStreamToTestRecord, self).status(
            test_id, test_status,
            test_tags=test_tags, runnable=runnable, file_name=file_name,
            file_bytes=file_bytes, eof=eof, mime_type=mime_type,
            route_code=route_code, timestamp=timestamp)

        if key and test_status in INTERIM_STATES:

            # XXX _StreamToTestRecord doesn't update the record status for
            #     interim results, which makes sense if the status is
            #     INPROGRESS (even if x-traceback has its status set to None,
            #     see ExtendedToStreamDecorator._convert). However it's not
            #     clear how we'd detect changes in the record.details, which
            #     we needed in order to trigger Repository.on_record_progress.
            record.set(status=test_status)

            self.on_test(record)
