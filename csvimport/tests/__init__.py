# import the test suites

from csvimport.tests.issue_tests import RegressionTest

from csvimport.tests.optional_tests import CommandArgsTest
from csvimport.tests.parse_tests import CommandParseTest
from csvimport.tests.constraint_tests import ConstraintTest

from csvimport.tests.performance_tests import PerformanceTest
from csvimport.tests.log_tests import LogTest
from csvimport.tests.admin_tests import AdminTest
