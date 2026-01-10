import time
import pytest
from conftest import load_db, das_setup, run, BackendType


@pytest.mark.parametrize("env", [
  BackendType.REDIS_MONGO, 
  BackendType.MORK_MONGO
  ], scope="class")
class TestEvolution:

  @pytest.fixture(scope="class", autouse=True)
  def setup_evolution(self, das_integration_env):
      load_db(None, "https://raw.githubusercontent.com/singnet/das/refs/heads/master/src/tests/assets/100K_sentences_10_words_a-f.metta")
      das_setup()

  def test_metta_services(self):
      result = run('!(das-services!)')
      assert len(result) == 1


  def test_metta_match_words(self):
      result = run('!(match &das (Contains (Sentence "abd cee cbd eab dfe fff abf cba cfa efe") (Word $W)) $W)')
      assert len(result) == 10

  def test_evolution_workflow(self):
      context = f'context-{time.time()}'
      result = run(f'!(das-create-context! {context} ((Contains $sentence1 $word1) ((0 $sentence1) ($sentence1 $word1)) ()))')
      assert len(result) == 1

      run('''(= (query) (Contains $sentence1 (Word "bbb")))''')
      run('''
  (= (str-length $s) (* ((py-dot "" len) $s) 1.0))
  (= (count-letters $s $c) (* ((py-dot $s count) $c) 1.0))
  (= (remove-spaces $s) ((py-dot $s replace) " " ""))
  (= (prep-sentence $s) (remove-spaces (index-atom $s 1)))
  (= 
    (ff $s $c) 
    (/ 
      (count-letters (prep-sentence $s) $c) 
      (str-length (prep-sentence $s))
    )
  )
  ''')
      run('''
  (=
    (correlation-queries)
    (
      (Contains $placeholder1 $word1)
    )
  )
  (=
    (correlation-replacements)
    (
      (placeholder1 sentence1)
    )
  )
  (=
    (correlation-mappings)
    (
      (sentence1 word1)
    )
  )
  ''')
      run('!(das-set-param! (max_generations 5))')
      result = run('''!(das-evolution! (!(query) (ff $sentence1 "c") !(correlation-queries) !(correlation-replacements) !(correlation-mappings)) $sentence1)''')
      assert len(result) > 0

      best_value = -1.0
      best_sentence = None
      for sentence in result:
          ff = run(f'!(ff {sentence} "c")')
          if ff and float(str(ff[0])) > best_value:
              best_value = float(str(ff[0]))
              best_sentence = sentence
      assert best_value >= 0.3