from datetime import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from pfnopt.storages.rdb.models import BaseModel
from pfnopt.storages.rdb.models import StudyModel
from pfnopt.storages.rdb.models import StudySystemAttributeModel
from pfnopt.storages.rdb.models import TrialModel
from pfnopt.storages.rdb.models import TrialSystemAttributeModel
from pfnopt.storages.rdb.models import TrialUserAttributeModel
from pfnopt.storages.rdb.models import VersionInfoModel
from pfnopt.structs import StudyTask
from pfnopt.structs import TrialState


@pytest.fixture
def session():
    # type: () -> Session

    engine = create_engine('sqlite:///:memory:')
    BaseModel.metadata.create_all(engine)
    return Session(bind=engine)


class TestStudySystemAttributeModel(object):

    @staticmethod
    def test_find_by_study_and_key(session):
        study = StudyModel(study_id=1, study_name='test-study')
        session.add(StudySystemAttributeModel(study_id=study.study_id, key='sample-key',
                                              value_json='1'))
        session.commit()

        assert '1' == StudySystemAttributeModel.find_by_study_and_key(study, 'sample-key',
                                                                      session).value_json
        assert StudySystemAttributeModel.find_by_study_and_key(study, 'not-found',
                                                               session) is None

    @staticmethod
    def test_where_study_id(session):
        sample_study = StudyModel(study_id=1, study_name='test-study')
        empty_study = StudyModel(study_id=2, study_name='test-study')

        session.add(StudySystemAttributeModel(study_id=sample_study.study_id, key='sample-key',
                                              value_json='1'))

        assert 1 == len(StudySystemAttributeModel.where_study_id(sample_study.study_id, session))
        assert 0 == len(StudySystemAttributeModel.where_study_id(empty_study.study_id, session))
        # Check the case of unknown study_id.
        assert 0 == len(StudySystemAttributeModel.where_study_id(-1, session))


class TestTrialModel(object):

    @staticmethod
    def test_default_datetime(session):
        # type: (Session) -> None

        datetime_1 = datetime.now()

        session.add(TrialModel(state=TrialState.RUNNING))
        session.commit()

        datetime_2 = datetime.now()

        trial_model = session.query(TrialModel).first()
        assert datetime_1 < trial_model.datetime_start < datetime_2
        assert trial_model.datetime_complete is None

    @staticmethod
    def test_count(session):
        # type: (Session) -> None

        study_1 = StudyModel(study_id=1, study_name='test-study-1')
        study_2 = StudyModel(study_id=2, study_name='test-study-2')

        session.add(TrialModel(study_id=study_1.study_id, state=TrialState.COMPLETE))
        session.add(TrialModel(study_id=study_1.study_id, state=TrialState.RUNNING))
        session.add(TrialModel(study_id=study_2.study_id, state=TrialState.RUNNING))
        session.commit()

        assert 3 == TrialModel.count(session)
        assert 2 == TrialModel.count(session, study=study_1)
        assert 1 == TrialModel.count(session, state=TrialState.COMPLETE)


class TestTrialUserAttributeModel(object):

    @staticmethod
    def test_find_by_trial_and_key(session):
        # type: (Session) -> None

        study = StudyModel(study_id=1, study_name='test-study')
        trial = TrialModel(study_id=study.study_id)

        session.add(TrialUserAttributeModel(trial_id=trial.trial_id, key='sample-key',
                                            value_json='1'))
        session.commit()

        attr = TrialUserAttributeModel.find_by_trial_and_key(trial, 'sample-key', session)
        assert attr is not None
        assert '1' == attr.value_json
        assert TrialUserAttributeModel.find_by_trial_and_key(trial, 'not-found', session) is None

    @staticmethod
    def test_where_study(session):
        # type: (Session) -> None

        study = StudyModel(study_id=1, study_name='test-study', task=StudyTask.MINIMIZE)
        trial = TrialModel(trial_id=1, study_id=study.study_id, state=TrialState.COMPLETE)

        session.add(study)
        session.add(trial)
        session.add(TrialUserAttributeModel(trial_id=trial.trial_id, key='sample-key',
                                            value_json='1'))
        session.commit()

        user_attributes = TrialUserAttributeModel.where_study(study, session)
        assert 1 == len(user_attributes)
        assert 'sample-key' == user_attributes[0].key
        assert '1' == user_attributes[0].value_json

    @staticmethod
    def test_where_trial(session):
        # type: (Session) -> None

        study = StudyModel(study_id=1, study_name='test-study', task=StudyTask.MINIMIZE)
        trial = TrialModel(trial_id=1, study_id=study.study_id, state=TrialState.COMPLETE)

        session.add(TrialUserAttributeModel(trial_id=trial.trial_id, key='sample-key',
                                            value_json='1'))
        session.commit()

        user_attributes = TrialUserAttributeModel.where_trial(trial, session)
        assert 1 == len(user_attributes)
        assert 'sample-key' == user_attributes[0].key
        assert '1' == user_attributes[0].value_json

    @staticmethod
    def test_all(session):
        # type: (Session) -> None

        study = StudyModel(study_id=1, study_name='test-study', task=StudyTask.MINIMIZE)
        trial = TrialModel(trial_id=1, study_id=study.study_id, state=TrialState.COMPLETE)

        session.add(TrialUserAttributeModel(trial_id=trial.trial_id, key='sample-key',
                                            value_json='1'))
        session.commit()

        user_attributes = TrialUserAttributeModel.all(session)
        assert 1 == len(user_attributes)
        assert 'sample-key' == user_attributes[0].key
        assert '1' == user_attributes[0].value_json


class TestTrialSystemAttributeModel(object):

    @staticmethod
    def test_find_by_trial_and_key(session):
        # type: (Session) -> None

        study = StudyModel(study_id=1, study_name='test-study')
        trial = TrialModel(study_id=study.study_id)

        session.add(TrialSystemAttributeModel(trial_id=trial.trial_id, key='sample-key',
                                              value_json='1'))
        session.commit()

        attr = TrialSystemAttributeModel.find_by_trial_and_key(trial, 'sample-key', session)
        assert attr is not None
        assert '1' == attr.value_json
        assert TrialSystemAttributeModel.find_by_trial_and_key(trial, 'not-found', session) is None

    @staticmethod
    def test_where_study(session):
        # type: (Session) -> None

        study = StudyModel(study_id=1, study_name='test-study', task=StudyTask.MINIMIZE)
        trial = TrialModel(trial_id=1, study_id=study.study_id, state=TrialState.COMPLETE)

        session.add(study)
        session.add(trial)
        session.add(TrialSystemAttributeModel(trial_id=trial.trial_id, key='sample-key',
                                              value_json='1'))
        session.commit()

        system_attributes = TrialSystemAttributeModel.where_study(study, session)
        assert 1 == len(system_attributes)
        assert 'sample-key' == system_attributes[0].key
        assert '1' == system_attributes[0].value_json

    @staticmethod
    def test_where_trial(session):
        # type: (Session) -> None

        study = StudyModel(study_id=1, study_name='test-study', task=StudyTask.MINIMIZE)
        trial = TrialModel(trial_id=1, study_id=study.study_id, state=TrialState.COMPLETE)

        session.add(TrialSystemAttributeModel(trial_id=trial.trial_id, key='sample-key',
                                              value_json='1'))
        session.commit()

        system_attributes = TrialSystemAttributeModel.where_trial(trial, session)
        assert 1 == len(system_attributes)
        assert 'sample-key' == system_attributes[0].key
        assert '1' == system_attributes[0].value_json

    @staticmethod
    def test_all(session):
        # type: (Session) -> None

        study = StudyModel(study_id=1, study_name='test-study', task=StudyTask.MINIMIZE)
        trial = TrialModel(trial_id=1, study_id=study.study_id, state=TrialState.COMPLETE)

        session.add(TrialSystemAttributeModel(trial_id=trial.trial_id, key='sample-key',
                                              value_json='1'))
        session.commit()

        system_attributes = TrialSystemAttributeModel.all(session)
        assert 1 == len(system_attributes)
        assert 'sample-key' == system_attributes[0].key
        assert '1' == system_attributes[0].value_json


class TestVersionInfoModel(object):

    @staticmethod
    def test_version_info_id_constraint(session):
        # type: (Session) -> None

        session.add(VersionInfoModel(schema_version=1, library_version='0.0.1'))
        session.commit()

        # Test check constraint of version_info_id.
        session.add(VersionInfoModel(version_info_id=2, schema_version=2, library_version='0.0.2'))
        pytest.raises(IntegrityError, lambda: session.commit())
