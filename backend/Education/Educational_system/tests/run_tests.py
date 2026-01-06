"""
Test Runner with HTML Reports
Run: python tests/run_tests.py
"""
import os
import sys
import django
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_system.settings')
django.setup()

import unittest
from HtmlTestRunner import HTMLTestRunner

# Import all test modules
from tests.test_authentication import TestAuthentication
from tests.test_user_management import TestUserManagement
from tests.test_content_management import TestContentManagement
from tests.test_student_advisor import TestStudentInteraction, TestAdvisorInteraction
from tests.test_evaluation import TestEvaluation
from tests.test_ai_features import TestAIFeatures
from tests.test_non_functional import TestNonFunctional, TestSecurity
from tests.test_live_sessions import TestLiveSessions
from tests.test_admin_system import TestAdminSystem
from tests.test_recurring_sessions import TestRecurringSessions


def create_test_suite():
    """Create test suite with all test cases"""
    suite = unittest.TestSuite()
    
    # Authentication Tests (TC-AUTH-001 to TC-AUTH-004)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAuthentication))
    
    # User Management Tests (TC-USER-001)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestUserManagement))
    
    # Content Management Tests (TC-CNT-001 to TC-CNT-003)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestContentManagement))
    
    # Student Interaction Tests (TC-STU-001, TC-STU-002)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStudentInteraction))
    
    # Advisor Interaction Tests (TC-ADV-001, TC-ADV-002)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAdvisorInteraction))
    
    # Evaluation Tests (TC-EVAL-001, TC-EVAL-002)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEvaluation))
    
    # AI Features Tests (TC-AI-001)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAIFeatures))
    
    # Non-Functional Tests (TC-NF-001)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNonFunctional))
    
    # Security Tests (TC-SEC-001)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSecurity))
    
    # Live Sessions Tests (TC-LS-001 to TC-LS-004)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLiveSessions))
    
    # Admin System Tests (TC-ADM-001 to TC-ADM-004)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAdminSystem))
    
    # Recurring Sessions Tests (TC-RS-001 to TC-RS-005)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRecurringSessions))
    
    return suite


if __name__ == '__main__':
    # Create reports directory
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate timestamp for report
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Create test suite
    suite = create_test_suite()
    
    # Run tests with HTML report
    runner = HTMLTestRunner(
        output=reports_dir,
        report_name=f'TestReport_{timestamp}',
        report_title='Complementary Education System - Test Report',
        descriptions=True,
        verbosity=2,
        combine_reports=True,
        add_timestamp=False
    )
    
    print("=" * 70)
    print("Running Test Suite for Complementary Education System")
    print("=" * 70)
    print(f"Report will be saved to: {reports_dir}")
    print("=" * 70)
    
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("Test Summary:")
    print(f"  Total Tests: {result.testsRun}")
    print(f"  Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failed: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("=" * 70)
