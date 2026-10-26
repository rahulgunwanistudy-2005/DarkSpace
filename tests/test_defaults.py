from pathlib import Path

from darkspace.defaults import Codebook, assign


def test_literal_rules_count_each_trait_once_and_do_not_infer_unwritten_features() -> None:
    codebook = Codebook.model_validate_json(Path("configs/default-codebook-v1.json").read_bytes())
    labels = assign("A task tracker tracks tasks and generates personalized reminders.", codebook)
    assert len(labels) == len(set(labels))
    assert {"tasks", "tracking", "generation", "personalization", "reminders"} <= set(labels)
    assert "quizzes" not in labels
    assert assign("A tool for people.", codebook) == ()
    assert "chat" not in assign("A habitat for small animals.", codebook)
    assert "tracking" in assign("TRACKING", codebook)
