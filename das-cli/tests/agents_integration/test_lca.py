import pytest
from conftest import load_db, das_setup, run, BackendType


@pytest.mark.parametrize("env",
    [
        BackendType.REDIS_MONGO,
        BackendType.MORK_MONGO
    ],
    scope="class"
)
class TestLCA:

    @pytest.fixture(scope="class", autouse=True)
    def setup_lca(self, das_integration_env):
        load_db(None, "https://raw.githubusercontent.com/singnet/das/refs/heads/master/src/tests/integration/cpp/data/animal_expressions.metta")

        das_setup()

        run('!(das-set-param! (max_answers 50))')


    def test_link_creation_and_matching(self):

        result = run('!(das-link-creation! (and (Evaluation (Predicate "is_mammal") (Concept $C1)) (Evaluation (Predicate "is_mammal") (Concept $C2))) (MyCustomRelationship $C1 $C2)(MyCustomRelationship $C2 $C1))')

        assert result

        result = run('!(match &das (MyCustomRelationship $C1 $C2) (MyCustomRelationship $C1 $C2))')

        assert len(result) > 0


    def test_equivalence_and_implication(self):

        result = run('!(das-link-creation! (and(Evaluation (Predicate "is_animal") (Concept $C1)) (Evaluation (Predicate "is_animal") (Concept $C2))(Evaluation (Predicate "is_mammal") (Concept $C1))(Evaluation (Predicate "is_mammal") (Concept $C2))(Evaluation (Predicate "two_legs") (Concept $C1))(Evaluation (Predicate "two_legs") (Concept $C2)))EQUIVALENCE_RELATION)')

        assert result

        result = run('!(match &das(Equivalence (Concept "human") (Concept "monkey")))')

        assert len(result) > 0
