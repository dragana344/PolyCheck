from analyzer.factory import CheckerFactory
from analyzer.languages.turkish.checker import TurkishChecker

CheckerFactory.register(TurkishChecker)
