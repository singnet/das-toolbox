import pytest
from conftest import load_db, das_setup, run, BackendType


@pytest.mark.parametrize("env", [
    BackendType.REDIS_MONGO, 
    BackendType.MORK_MONGO
    ], scope="class")
class TestQuery:
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, das_integration_env):
        load_db(None, "https://raw.githubusercontent.com/singnet/das/refs/heads/master/src/tests/integration/cpp/data/animal_expressions.metta")
        das_setup()

    def test_metta_services(self):
        result = run('!(das-services!)')
        assert result
        
        
    def test_metta_match_evaluation(self):
        result = run('!(match &das (Evaluation $P $C) (Evaluation $P $C))')
        print(result)
        assert len(result) == 26

    def test_metta_match_animal(self):
        result = run('''
    !(match 
            &das 
            (or 
            (Evaluation (Predicate "is_animal") (Concept $C)) 
            (Evaluation (Predicate "two_legs") (Concept $C))) 
            $C)
    ''')
        print(result)
        assert len(result) == 8



    def test_metta_match_mammal_four_legs(self):
        result = run('''
        !(match 
                &das 
                (and 
                (Evaluation (Predicate "is_mammal") (Concept $C)) 
                (Evaluation (Predicate "four_legs") (Concept $C))) 
                $C)
        ''')
        print(result)
        assert len(result) == 1

    def test_metta_match_complex(self):
        result = run('''
    !(match 
            &das
            (and
                (and
                    (Evaluation (Predicate "is_animal") (Concept $C))
                    (Evaluation (Predicate "is_reptile") (Concept $C)))
                (and
                    (Evaluation (Predicate "is_dinosaur") (Concept $C))
                    (and
                        (Evaluation (Predicate "has_horns") (Concept $C))
                        (Evaluation (Predicate "four_legs") (Concept $C)))))
            $C)
    ''')
        print(result)
        assert len(result) == 1

    def test_metta_match_triceratops(self):
        result = run('!(match &das (Evaluation (Predicate $P) (Concept "triceratops")) $P)')
        print(result)
        assert len(result) == 5

    def test_metta_match_animal_legs(self):
        result = run('''
    !(match 
            &das 
            (and
            (Evaluation (Predicate "is_animal") (Concept $C)) 
            (or
                (Evaluation (Predicate "two_legs") (Concept $C))
                (Evaluation (Predicate "no_legs") (Concept $C))))
            $C)
    ''')
        print(result)
        assert len(result) == 4