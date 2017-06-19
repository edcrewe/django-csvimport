# No need to import tests
try:
    from csvimport.tests.parse_tests import CommandParseTest
    from csvimport.tests.log_tests import LogTest
    from csvimport.tests.optional_tests import CommandArgsTest
    from csvimport.tests.constraint_tests import ConstraintTest
    from csvimport.tests.performance_tests import PerformanceTest    
except:
    # loading csvimport tests as an app to manually test the models
    # but test import for testing above breaks app startup in 1.9+
    pass
