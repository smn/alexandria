from alexandria.dsl.core import MenuSystem, prompt, end
from alexandria.dsl.validators import pick_one

def get_menu():
    return MenuSystem(
        prompt('What is your favorite programming language?', options=(
        'java', 'c', 'python', 'ruby', 'javascript', 'php', 'other'
        ), validator=pick_one),
        prompt('What is your favorite development operating system?', options=(
            'windows', 'apple', '*nix', 'other'
        ), validator=pick_one),
        prompt('What is your favorite development environment?', options=(
            'netbeans', 'eclipse', 'vim', 'emacs', 'textmate', 'notepad'
        ), validator=pick_one),
        end('Thanks! You have completed the quiz')
    )