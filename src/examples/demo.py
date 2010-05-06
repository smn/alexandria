from alexandria.dsl.core import MenuSystem, prompt, end
from alexandria.dsl.validators import pick_one

def get_menu():
    return MenuSystem(
        prompt('What is your favorite browser?', options=(
        'IE', 'Firefox', 'Chrome', 'Safari', 'Opera', 'Lynx', 'other'
        ), validator=pick_one),
        prompt('What is your favorite version control system?', options=(
            'svn', 'git', 'darcs', 'mercurial', 'cvs'
        ), validator=pick_one),
        prompt('What is your favorite development environment?', options=(
            'netbeans', 'eclipse', 'vim', 'emacs', 'textmate', 'notepad'
        ), validator=pick_one),
        end('Thanks! You have completed the quiz')
    )