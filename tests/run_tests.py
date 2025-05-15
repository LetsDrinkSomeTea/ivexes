import unittest
import sys
import os

# Add the project root to the Python path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

if __name__ == '__main__':
    # Discover and run all tests in the tests directory
    start_dir = os.path.dirname(__file__)
    test_suite = unittest.TestLoader().discover(start_dir=start_dir)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with non-zero status if there were failures
    sys.exit(not result.wasSuccessful())