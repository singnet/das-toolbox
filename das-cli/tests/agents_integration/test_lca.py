import pytest
from conftest import load_db, das_setup, run, BackendType
import time


@pytest.mark.parametrize("env", [
    BackendType.REDIS_MONGO, 
    BackendType.MORK_MONGO
    ], scope="class")
class TestLCA:

    @pytest.fixture(scope="class", autouse=True)
    def setup_lca(self, das_integration_env):
        load_db(None, "https://raw.githubusercontent.com/singnet/das/refs/heads/master/src/tests/integration/cpp/data/animal_expressions.metta")
        das_setup()
        run('!(das-set-param! (max_answers 5))')


    def test_link_creation_and_matching(self):
        result = run('''
        !(das-link-creation! 
            (and 
                (Evaluation (Predicate "is_mammal") (Concept $C1)) 
                (Evaluation (Predicate "is_mammal") (Concept $C2))
            ) 
            (MyCustomRelationship $C1 $C2) 
            (MyCustomRelationship $C2 $C1)
        )
        ''')
        assert result
        result = run('!(match &das (MyCustomRelationship $C1 $C2) (MyCustomRelationship $C1 $C2))')
        assert len(result) == 5

    def test_equivalence_and_implication(self):
        result = run('!(das-link-creation! (and (Concept $C1) (Concept $C2)) EQUIVALENCE_RELATION)')
        result = run('!(match &das (Equivalence (Concept $C1) (Concept $C2)) (Equivalence (Concept $C2) (Concept $C1)))')
        assert len(result) > 0

        result = run('!(das-link-creation! (and (Predicate $P1) (Predicate $P2)) IMPLICATION_RELATION)')
        result = run('!(match &das (Implication (Predicate $P1) (Predicate $P2)) (Implication (Predicate $P2) (Predicate $P1)))')
        assert len(result) > 0