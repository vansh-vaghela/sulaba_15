def star_mark_check(self):
        token_url = hp_config['HP_STARMARKED_TOKEN_URL']
        test_api_url = hp_config['HP_STARMARKED_API_URL']

        starmark_access_key = self.env["ir.config_parameter"].sudo().get_param("isha_hr.hr_star_mark_api")

        api_call_headers = {'Authorization': 'Bearer ' + starmark_access_key}
        input = {
            "params": {
                "name": self.partner_name,
                "phone": self.partner_mobile,
                "email": self.email_from,
                "lenient_search": True}
        }
        try:
            api_call_response = requests.post(test_api_url, json=input, headers=api_call_headers)
            # print(test_api_url)
            # print(api_call_response)
            api_call_response_json = json.loads(api_call_response.text)
            # print(api_call_response_json)

            if '401 UNAUTHORIZED' in api_call_response.text:
                client_id = hp_config['HP_STARMARKED_CLIENT_ID']
                client_secret = hp_config['HP_STARMARKED_CLIENT_SECRET']
                # step A, B - single call with client credentials as the basic auth header - will return access_token
                data = {'grant_type': 'client_credentials'}
                access_token_response = requests.post(token_url, data=data, verify=False, allow_redirects=False,
                                                      auth=(client_id, client_secret))
                print(access_token_response.headers)
                print(access_token_response.text)
                tokens = json.loads(access_token_response.text)
                print("access token: " + tokens['access_token'])
                # step B - with the returned access_token we can make as many calls as we want

                api_call_headers = {'Authorization': 'Bearer ' + tokens['access_token']}
                input = {
                    "params": {
                        "name": self.partner_name,
                        "phone": self.partner_mobile,
                        "email": self.email_from,
                        "lenient_search": True}
                }
                api_call_response = requests.post(test_api_url, json=input, headers=api_call_headers, verify=False)
                # print(test_api_url)
                # print(api_call_response)
                api_call_response_json = json.loads(api_call_response.text)
                # print(api_call_response_json)
                self.env["ir.config_parameter"].sudo().set_param("isha_hr.hr_star_mark_api", tokens['access_token'])

            if api_call_response_json['result']:
                self.write({'is_star_marked': 'NO',
                            'star_mark_color': '',
                            'severity': ''})
                for result in api_call_response_json['result']:
                    if result['isStarMarked']:
                        self.write({'is_star_marked': 'YES',
                                    'star_mark_color': result['color'],
                                    'severity': result['severity']})
                        if result['dnaInfo']:
                            self.env['hr.applicant_star_marked'].sudo().search([('applicant_id', '=', self.id)]).unlink()
                            for dnaInfo in result['dnaInfo']:
                                value1 = dnaInfo['values'][0] if len(dnaInfo['values']) > 0 else None
                                value2 = dnaInfo['values'][1] if len(dnaInfo['values']) > 1 else None
                                value3 = dnaInfo['values'][2] if len(dnaInfo['values']) > 2 else None
                                value4 = dnaInfo['values'][3] if len(dnaInfo['values']) > 3 else None
                                value5 = dnaInfo['values'][4] if len(dnaInfo['values']) > 4 else None
                                self.env['hr.applicant_star_marked'].sudo().create({'applicant_id': self.id,
                                                                            'category_name': dnaInfo['categoryName'],
                                                                             'value1': value1,
                                                                             'value2': value2,
                                                                             'value3': value3,
                                                                             'value4': value4,
                                                                             'value5': value5,
                                                                             'remarks': dnaInfo['remarks']})
            else:
                self.env['hr.applicant_star_marked'].sudo().search([('applicant_id', '=', self.id)]).unlink()
                self.write({'is_star_marked': 'NO',
                            'star_mark_color': '',
                            'severity': ''})
        except Exception as e:
            logging.exception('Starmark Check Exception occured.')
    selectable_fields = ['name', 'partner_name', 'job_id', 'application_id', 'requesting_department_id',
                         'resource_category', 'connected_status', 'assignment1_status', 'assignment2_status', 'first_interview_status',
                         'second_interview_status', 'final_interview_status', 'partner_id', 'partner_phone', 'partner_mobile',
                         'email_from', 'dob', 'gender', 'marital_status', 'nationality', 'address', 'type_id', 'qualification',
                         'experience', 'functional_areas', 'skill_competencies', 'other_interests', 'categ_ids', 'user_id',
                         'source_id', 'prescreening_id', 'assignment1_id', 'assignment2_id', 'first_interview_id', 'second_interview_id',
                         'survey_id', 'is_meditator', 'is_star_marked', 'star_marked_color', 'severity', 'job_location',
                         'reason_for_change', 'done_isha_program', 'stay_in_ashram', 'any_kind_job', 'duration_with_isha',
                         'about_us', 'salary_expected', 'salary_proposed', 'notice_period', 'availability', 'joining_formalities_id',
                         'template_id_2', 'employee_id', 'links_of_interest', 'upload_cv_resume', 'offer_letter', 'offer_acceptance',
                         'portal_applicant_comments', 'passport_photo', 'identity_proof', 'address_proof', 'degree_certificate',
                         'experience_certificate', 'relieving_order', 'last_drawn_salary', 'bank_account_proof',
                         'stage_id','active','create_uid','create_date','write_uid','write_date','first_interview_response_state',
                         'second_interview_response_state','survey_response_state','prescreening_date','connected_date',
                         'first_interview_date','last_interview_date','offer_issued_date','offer_accepted_date','offer_declined_date',
                         'onboarded_date','decline_reason_date','languages','hp_starmarked','hp_meditator','sp_completed','employee_id',
                         'is_source_validated']
