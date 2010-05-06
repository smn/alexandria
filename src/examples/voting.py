from alexandria.dsl.core import MenuSystem, prompt, end
from alexandria.dsl.validators import pick_one

def get_menu():
    return MenuSystem(
        prompt('Which solution is your favorite?', options=(
        'Tbl1-Edu', 
        'Tbl2-Edu', 
        'Tbl3-Commun. info', 
        'Tbl4-Mob. consc.', 
        'Tbl5-Health 1', 
        'Tbl5-Health 2', 
        'Tbl6-Sec',
        'Tbl7-Sec',
        'Tbl8-Sec',
        'Tbl8-Edu'
        ), validator=pick_one),
        end('Thanks for voting!')
    )