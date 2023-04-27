import gen_applications as app
import gen_applicant

def test_get_dummy_application_type():
    app_type = app.get_dummy_application_type()
    application_types = ["CHECKING", "SAVINGS", "CHECKING_AND_SAVINGS", "CREDIT_CARD", "LOAN"]
    assert app_type in application_types

def test_get_dummy_deposit_account_num():
    depo_acc_num = app.get_dummy_deposit_account_num()
    assert len(depo_acc_num) == 12
    assert isinstance(depo_acc_num, str)

def test_create_application():
    new_applicant = gen_applicant.Applicant()
    application = app.create_application(new_applicant)
    assert application.get('applicationType') in ["CHECKING", "SAVINGS", "CHECKING_AND_SAVINGS", "CREDIT_CARD", "LOAN"]
    assert application.get('noNewApplicants') == False
    assert isinstance(application.get('applicants')[0], dict)
    assert isinstance(application.get('applicationAmount'), int) 
    assert application.get('applicationAmount') >= 16000 and application.get('applicationAmount') <= 10000000
    assert isinstance(application.get('cardOfferId'), int) 
    assert application.get('cardOfferId') >= 0 and application.get('cardOfferId') <= 108
    assert isinstance(application.get('depositAccountNumber'), str)

def test_get_application():
    applicants = gen_applicant.gen_applicants_by_amount(10)
    applications = app.get_applications(applicants)
    assert len(applications) == 10
    assert isinstance(applications, list)

def test_post_requests():
    applicants = gen_applicant.gen_applicants_by_amount(10)
    applications = app.get_applications(applicants)
    info_list, response_codes = app.post_requests(applications, app.hit_api_applications)
    assert len(response_codes) == 10
    result = all(code != None for code in response_codes)
    assert result == True