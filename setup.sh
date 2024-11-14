#!/bin/bash

# Step 1: Check if virtual environment exists
if [ -d "venv" ]; then
  echo "Activating existing virtual environment..."
  source venv/bin/activate
else
  echo "Virtual environment not found. Please create one first."
  exit 1
fi

# Step 2: Install dependencies
echo "Installing dependencies..."
pip install flask8 pytest black

# Step 3: Change permission of setup.sh
chmod 777 setup.sh

# Step 4: Recursively search for tests.py file in the project directory
echo "Searching for tests.py..."
TEST_PATH=$(find . -type f -name "tests.py")

# If no tests.py is found, exit the script
if [ -z "$TEST_PATH" ]; then
  echo "tests.py not found. Exiting setup..."
  exit 1
fi

echo "Found tests.py at $TEST_PATH"

# Step 5: Write the specified content to the pre-push hook
echo "Updating pre-push hook..."

cat <<EOL > .git/hooks/pre-push
#!/bin/bash

echo "Searching for tests.py..."
TEST_PATH=\$(find . -type f -name "tests.py")

# If no tests.py is found, exit the script
if [ -z "\$TEST_PATH" ]; then
  echo "tests.py not found. Exiting setup..."
  exit 1
fi

echo "Found tests.py at \$TEST_PATH"

# Run tests with pytest on the found tests.py
echo "Running unit tests with pytest..."

# Run pytest on the specific test file and output results to result.log
python3 -m pytest "\$TEST_PATH" > result.log

# Display pytest output in terminal for visibility
cat result.log

TEST_RESULT=\$?

# If pytest fails (non-zero exit code), abort the process
if [ \$TEST_RESULT -ne 0 ]; then
  echo "Tests failed. Setup aborted."
  exit 1  # This stops the setup if there are test failures
fi

echo "Tests passed. Proceeding with push setup."
EOL

# Step 6: Set execute permission for pre-push hook
chmod u+x .git/hooks/pre-push

echo "Setup complete. You can now use 'git push'."
