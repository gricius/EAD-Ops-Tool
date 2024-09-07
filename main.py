# main.py is the entry point for the application. 
# It imports the create_main_window function from the gui module and calls it 
# when the script is run. This function creates the main window for the application,
#  which contains the user interface elements and functionality. 
# The if __name__ == "__main__": block ensures that the create_main_window function 
# is only called when the script is run directly, 
# and not when it is imported as a module in another script. 
# This separation of concerns helps to keep the code organized and maintainable.
# Application EAD Ops Tool entry point
from gui import create_main_window

if __name__ == "__main__":
    create_main_window()
