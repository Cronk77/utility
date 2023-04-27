import gen_bank_branch
from gen_user import create_users, register_users, login

def test_get_bank():
    bank = gen_bank_branch.get_bank()
    assert isinstance(bank.get('routingNumber'), str)
    assert len(bank.get('routingNumber')) == 9
    assert isinstance(bank.get('address'), str)
    assert isinstance(bank.get('city'), str)
    assert isinstance(bank.get('state'), str)
    assert isinstance(bank.get('zipcode'), str)

def test_get_branch():
    branch = gen_bank_branch.get_branch(1)
    assert isinstance(branch.get('name'), str)
    assert isinstance(branch.get('address'), str)
    assert isinstance(branch.get('city'), str)
    assert isinstance(branch.get('state'), str)
    assert isinstance(branch.get('zipcode'), str)
    assert isinstance(branch.get('bankID'), int)

def test_gen_bank():
    user_list, _ = create_users(1, 'admin')
    _, _, update_users = register_users(user_list)
    user_name = update_users[0].get('username')
    password = update_users[0].get('password')
    _, authorization_token = login(user_name, password)
    resp, resp_info = gen_bank_branch.gen_bank(authorization_token)
    assert  str(resp) == "<Response [201]>"
    assert resp_info != None

def test_gen_branch():
    user_list, _ = create_users(1, 'admin')
    _, _, update_users = register_users(user_list)
    user_name = update_users[0].get('username')
    password = update_users[0].get('password')
    _, authorization_token = login(user_name, password)
    _, resp_info = gen_bank_branch.gen_bank(authorization_token)
    bank_id = resp_info.get('id')
    resp, branch_info = gen_bank_branch.gen_branch(authorization_token, bank_id)
    assert  str(resp) == "<Response [201]>"

