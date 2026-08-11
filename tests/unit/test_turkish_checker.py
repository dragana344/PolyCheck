"""
Unit tests for TurkishChecker.

All test sentences use real Turkish text.  Each test targets one specific
error type.  Turkish-specific rules (apostrophe, question particle,
herşey/birçok compounds, number suffixes) get positive, negative, and
false-positive-guard cases.
"""

import pytest

from analyzer.factory import CheckerFactory


@pytest.fixture(scope="module")
def tr():
    return CheckerFactory.get("tr")


def errors_of(checker, sentence, error_type):
    return [e for e in checker.check_sentence(sentence)
            if e.error_type == error_type]


# ─── Shared rules sanity ──────────────────────────────────────────────────────

class TestTurkishSharedRules:
    def test_detects_lowercase_start(self, tr):
        assert errors_of(tr, "bugün hava çok güzel.", "Capitalization")

    def test_detects_double_space(self, tr):
        assert errors_of(tr, "Bugün  hava çok güzel.", "DoubleSpace")

    def test_no_repeated_word_flag_for_reduplication(self, tr):
        # Turkish reduplications (yavaş yavaş, etc.) are grammatically valid.
        # RepeatedWordRule is intentionally excluded from Turkish.
        assert not errors_of(tr, "yavaş yavaş ilerliyordu.", "RepeatedWord")

    def test_clean_sentence_has_no_structural_errors(self, tr):
        errors = tr.check_sentence("Bugün hava çok güzel.")
        structural = [e for e in errors if e.error_type in {
            "Capitalization", "DoubleSpace", "RepeatedWord",
            "MissingEndPunctuation", "SpaceBeforePunctuation",
        }]
        assert structural == []


# ─── Proper noun / abbreviation apostrophe ────────────────────────────────────

class TestTurkishProperNounApostrophe:
    def test_detects_city_missing_apostrophe(self, tr):
        assert errors_of(tr, "Ankaraya yarın gidiyorum.", "ProperNounApostrophe")

    def test_detects_abbreviation_missing_apostrophe(self, tr):
        assert errors_of(tr, "TBMMde yeni bir yasa kabul edildi.",
                         "ProperNounApostrophe")

    def test_detects_caps_only_abbreviation_ab(self, tr):
        assert errors_of(tr, "ABye üyelik süreci devam ediyor.",
                         "ProperNounApostrophe")

    def test_detects_instrumental_suffix(self, tr):
        assert errors_of(tr, "Ahmetle sinemaya gittik.", "ProperNounApostrophe")

    def test_detects_accusative_suffix(self, tr):
        assert errors_of(tr, "Ankarayı çok özledim.", "ProperNounApostrophe")

    def test_no_error_with_apostrophe(self, tr):
        assert errors_of(tr, "Ankara'ya yarın gidiyorum.",
                         "ProperNounApostrophe") == []

    def test_no_error_for_abla_at_sentence_start(self, tr):
        # 'Abla' must NOT be parsed as abbreviation AB + suffix 'la'.
        assert errors_of(tr, "Abla bana yardım etti.",
                         "ProperNounApostrophe") == []

    def test_no_error_for_derivational_suffix(self, tr):
        assert errors_of(tr, "Ankaralı arkadaşım geldi.",
                         "ProperNounApostrophe") == []


# ─── Question particle ────────────────────────────────────────────────────────

class TestTurkishQuestionParticle:
    def test_detects_joined_particle(self, tr):
        assert errors_of(tr, "Bunu gerçekten yapabilecekmisin?",
                         "QuestionParticle")

    def test_no_error_for_separate_particle(self, tr):
        assert errors_of(tr, "Geldin mi?", "QuestionParticle") == []

    def test_no_error_for_short_stem_words(self, tr):
        # 'cami' and 'resmi' end in -mi but are ordinary words.
        assert errors_of(tr, "Resmi kurumlar cami inşaatını onayladı.",
                         "QuestionParticle") == []


# ─── Her şey / birçok / bir şey compounds ─────────────────────────────────────

class TestTurkishHerSey:
    def test_detects_joined_hersey(self, tr):
        assert errors_of(tr, "Herşey yolunda.", "HerSey")

    def test_detects_suffixed_hersey(self, tr):
        assert errors_of(tr, "Herşeyi denedim ama olmadı.", "HerSey")
        assert errors_of(tr, "Herşeyden önce sağlık gelir.", "HerSey")

    def test_no_error_for_separate_her_sey(self, tr):
        assert errors_of(tr, "Her şey yolunda.", "HerSey") == []
        assert errors_of(tr, "Her şeyi denedim.", "HerSey") == []

    def test_message_contains_heuristic_label(self, tr):
        errors = errors_of(tr, "Herşey bitti.", "HerSey")
        assert errors and "[HEURISTIC]" in errors[0].message


class TestTurkishBircok:
    def test_detects_separate_bir_cok(self, tr):
        assert errors_of(tr, "Bir çok insan toplantıya geldi.", "Bircok")

    def test_detects_joined_birsey(self, tr):
        assert errors_of(tr, "Sana birşey söyleyeceğim.", "Bircok")

    def test_detects_suffixed_birsey(self, tr):
        assert errors_of(tr, "Birşeyler ters gidiyor.", "Bircok")

    def test_no_error_for_correct_forms(self, tr):
        assert errors_of(tr, "Birçok insan toplantıya geldi.", "Bircok") == []
        assert errors_of(tr, "Sana bir şey söyleyeceğim.", "Bircok") == []

    def test_no_error_for_bir_cokluk(self, tr):
        # 'bir çokluk' is a legitimate phrase (a multitude / a plurality).
        assert errors_of(tr, "Matematikte bir çokluk kavramı vardır.",
                         "Bircok") == []


# ─── Number suffix apostrophe ─────────────────────────────────────────────────

class TestTurkishNumberSuffix:
    def test_detects_year_suffix(self, tr):
        assert errors_of(tr, "Toplantı 2024te yapılacak.", "NumberSuffix")

    def test_detects_hour_suffix(self, tr):
        assert errors_of(tr, "Saat 10da buluşalım.", "NumberSuffix")

    def test_no_error_with_apostrophe(self, tr):
        assert errors_of(tr, "Toplantı 2024'te yapılacak.",
                         "NumberSuffix") == []

    def test_no_error_for_uppercase_tech_terms(self, tr):
        assert errors_of(tr, "Yeni telefon 5G destekliyor.",
                         "NumberSuffix") == []
        assert errors_of(tr, "Dosya 25MB boyutunda.", "NumberSuffix") == []

    def test_no_error_for_lowercase_units(self, tr):
        assert errors_of(tr, "Paket 5kg geliyor.", "NumberSuffix") == []
        assert errors_of(tr, "Masa 80cm yüksekliğinde.", "NumberSuffix") == []


# ─── General contract ─────────────────────────────────────────────────────────

class TestTurkishCheckerContract:
    def test_language_code(self, tr):
        assert tr.language_code == "tr"

    def test_check_sentence_always_returns_list(self, tr):
        assert isinstance(tr.check_sentence("Merhaba dünya."), list)

    def test_all_messages_have_heuristic_prefix(self, tr):
        errors = tr.check_sentence("herşey  TBMMde 2024te konuşuldumu bilmiyorum")
        assert errors
        for e in errors:
            assert e.message.startswith("[HEURISTIC]")
