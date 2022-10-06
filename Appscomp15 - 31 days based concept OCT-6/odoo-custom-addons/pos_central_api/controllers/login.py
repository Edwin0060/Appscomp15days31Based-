import json
import logging
import functools
import werkzeug.wrappers

from odoo import http
from odoo.addons.pos_central_api.models.common import invalid_response, valid_response
from odoo.exceptions import AccessDenied, AccessError
from odoo.http import request

_logger = logging.getLogger(__name__)


def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get("access_token")
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)
        access_token_data = request.env["api.access_token"].sudo().search([("token", "=", access_token)],
                                                                          order="id DESC", limit=1)

        if access_token_data.find_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response("access_token", "token seems to have expired or invalid", 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        return func(self, *args, **kwargs)

    return wrap


class AccessToken(http.Controller):
    @http.route("/api/login", methods=["GET"], type="http", auth="none", csrf=False)
    def api_login(self, **post):
        """The token URL to be used for getting the access_token:

        Args:
            **post must contain login and password.
        Returns:

            returns https response code 404 if failed error message in the body in json format
            and status code 202 if successful with the access_token.
        Example:
           import requests

           headers = {'content-type': 'text/plain', 'charset':'utf-8'}

           data = {
               'login': 'admin',
               'password': 'admin',
               'db': 'galago.ng'
            }
           base_url = 'http://odoo.ng'
           eq = requests.post(
               '{}/api/auth/token'.format(base_url), data=data, headers=headers)
           content = json.loads(req.content.decode('utf-8'))
           headers.update(access-token=content.get('access_token'))

        If you would like to use body to send the data you can do the following:
            payload = request.httprequest.data.decode()
            payload = json.loads(payload)
            db, username, password = (
                payload.get("db"),
                payload.get("login"),
                payload.get("password"),
            )
        """
        params = ["db", "login", "password"]
        params = {key: post.get(key) for key in params if post.get(key)}
        db, username, password = (
            params.get("db"),
            post.get("login"),
            post.get("password"),
        )
        _credentials_includes_in_body = all([db, username, password])
        if not _credentials_includes_in_body:
            # The request post body is empty the credetials maybe passed via the headers.
            headers = request.httprequest.headers
            db = headers.get("db")
            username = headers.get("login")
            password = headers.get("password")
            _credentials_includes_in_headers = all([db, username, password])
            if not _credentials_includes_in_headers:
                # Empty 'db' or 'username' or 'password:
                return invalid_response(
                    "missing error", "either of the following are missing [db, username,password]", 403,
                )
        # Login in odoo database:
        try:
            request.session.authenticate(db, username, password)
        except AccessError as aee:
            return invalid_response("Access error", "Error: %s" % aee.name)
        except AccessDenied as ade:
            return invalid_response("Access denied", "Login, password or db invalid")
        except Exception as e:
            # Invalid database:
            info = "The database name is not valid {}".format((e))
            error = "invalid_database"
            _logger.error(info)
            return invalid_response("wrong database name", error, 403)

        uid = request.session.uid
        # odoo login failed:
        if not uid:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)

        # Generate tokens
        access_token = request.env["api.access_token"].find_or_create_token(user_id=uid, create=True)
        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "uid": uid,
                    # "user_context": request.session.get_context() if uid else {},
                    # "company_id": request.env.user.company_id.id if uid else None,
                    # "company_ids": request.env.user.company_ids.ids if uid else None,
                    # "partner_id": request.env.user.partner_id.id,
                    "access_token": access_token,
                    # "company_name": request.env.user.company_name,
                    # "country": request.env.user.country_id.name,
                    # "contact_address": request.env.user.contact_address,
                }
            ),
        )

    @http.route("/api/login/token_api_key", methods=["GET"], type="http", auth="none", csrf=False)
    def api_login_api_key(self, **post):
        # The request post body is empty the credetials maybe passed via the headers.
        headers = request.httprequest.headers
        db = headers.get("db")
        api_key = headers.get("api_key")
        _credentials_includes_in_headers = all([db, api_key])
        if not _credentials_includes_in_headers:
            # Empty 'db' or 'username' or 'api_key:
            return invalid_response(
                "missing error", "either of the following are missing [db ,api_key]", 403,
            )
        # Login in odoo database:
        user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)
        # request.session.authenticate(db, username, api_key)
        if not user_id:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)

        uid = user_id
        user_obj = request.env['res.users'].sudo().browse(int(uid))

        # Generate tokens
        access_token = request.env["api.access_token"].find_or_create_token(user_id=uid, create=True)
        # Successful response:
        return werkzeug.wrappers.Response(
            status=200,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                {
                    "uid": uid,
                    # "user_context": request.session.get_context() if uid else {},
                    # "company_id": user_obj.company_id.id if uid else None,
                    # "company_ids": user_obj.company_ids.ids if uid else None,
                    # "partner_id": user_obj.partner_id.id,
                    "access_token": access_token,
                    # "company_name": user_obj.company_name,
                    # "country": user_obj.country_id.name,
                    # "contact_address": user_obj.contact_address,
                }
            ),
        )

    @validate_token
    @http.route("/hello", methods=["POST"], type="http", auth="none", csrf=False)
    def hello_world(self, **post):
        return 'Helloo world'

    @validate_token
    @http.route("/get/params", methods=["POST"], type="http", auth="none", csrf=False)
    def hello_world(self, **post):
        user_id = request.uid
        user_obj = request.env['res.users'].browse(user_id)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        proj_name = payload.get("proj_name")
        proj_obj = request.env['project.project']
        new_proj = proj_obj.with_user(user_obj).create({
            'name': proj_name,
        })
        if new_proj:
            return valid_response([{"proje_id": new_proj.id, "message": "Project created successfully"}], status=201)
        return proj_name

    @validate_token
    @http.route("/api/project/create", methods=["POST"], type="http", auth="none", csrf=False)
    def create_project(self, **post):
        print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
        user_id = request.uid
        user_obj = request.env['res.users'].browse(user_id)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        proj_name = payload.get("proj_name")
        proj_obj = request.env['project.project']
        new_proj = proj_obj.with_user(user_obj).create({
            'name': proj_name,
        })
        if new_proj:
            return valid_response([{"proje_id": new_proj.id, "message": "Project created successfully"}], status=201)

    @validate_token
    @http.route("/api/project/write", methods=["POST"], type="http", auth="none", csrf=False)
    def create_project(self, **post):
        user_id = request.uid
        user_obj = request.env['res.users'].browse(user_id)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        proj_id = payload.get("proj_id")
        proj_write_name = payload.get("proj_name")

        proj_obj = request.env['project.project']
        # updated_proj = request.env.with_user(user_obj).searh([('id', '=', int(proj_id))])
        updated_proj = proj_obj.browse(int(proj_id))
        is_updated = updated_proj.with_user(user_obj).write({
            'name': proj_write_name,
        })
        if is_updated:
            return valid_response([{"proje_id": proj_id, "message": "Project updated successfully"}], status=200)

    # return werkzeug.wrappers.Response(
    #     status=200,
    #     content_type="application/json; charset=utf-8",
    #     headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
    # )
    #
    # @validate_token
    # @http.route("/api/all_stages/read", methods=["POST"], type="http", auth="none", csrf=False)
    # def all_project_stages(self, **post):
    #     user_id = request.uid
    #     user_obj = request.env['res.users'].browse(user_id)
    #
    #     stages_obj = request.env['project.task.type']
    #     read_stages = stages_obj.with_user(user_obj).search([])
    #     stages_list = []
    #     for crm in read_stages:
    #         value_dict = {}
    #         for f in crm._fields:
    #             try:
    #                 value_dict[f] = str(getattr(crm, f))
    #             except AccessError as aee:
    #                 print(aee)
    #         stages_list.append(value_dict)
    #
    #     return werkzeug.wrappers.Response(
    #         status=200,
    #         content_type="application/json; charset=utf-8",
    #         headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
    #         response=json.dumps(
    #             stages_list
    #         ),
    #     )

  #  @validate_token
   # @http.route("/api/pos/sale_details", methods=["POST"], type="http", auth="none", csrf=False)
   # def all_project_stages(self, **post):
   #     payload = request.httprequest.data.decode()
   #     payload = json.loads(payload)
   #     date_from = payload.get("date_from")
   #     date_to = payload.get("date_to")
   #     # pos_sale = request.env['pos.order'].search_read()
   #     print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT", post)
   #     domain = [('date_order', '>=', date_from), ('date_order', '<=', date_to)]
   #     pos_sale = request.env['pos.order'].search_read(domain)
   #     print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD", date_from, date_to)
   #     # pos_sale_list = []
   #     # for pos in pos_sale:
   #     print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS", pos_sale)
   #     if pos_sale:
   #         pos_sales_vals = [{
   #             "LOCATION_CODE": 1,
   #             "TERMINAL_ID": 1,
   #             "SHIFT_NO": 1,
   #             'name': pos.get('name'),
   #             'RCPT_NUM': pos.get('pos_reference'),
   #             'INV_AMT': pos.get('amount_total'),
   #             'TAX_AMT': pos.get('amount_tax'),
   #             'RET_AMT': pos.get('amount_return'),
   #             'OP_CUR': pos.get('pricelist_id.currency_id.name'),
   #             'DISCOUNT': pos.get('currency_id.name'),
   #             'RCPT_DT': pos.get('date_order'),
   #         } for pos in pos_sale]
            # for p in pos_sale:
            #     print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",p)
            # name = pos.get('name')
            # print("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN", name)
            # pos_sale_list.append(name)
            # value_dict = {}
            # for f in pos.user_id:
            #     value_dict = f
            # pos_sale_list.append(value_dict)
            # for f in pos._fields:
            #     try:
            #         value_dict[f] = str(getattr(pos, f))
            #     except AccessError as aee:
            #         print(aee)
            # pos_sale_list.append(value_dict)

   #        return werkzeug.wrappers.Response(
   #             status=200,
   #             content_type="application/json; charset=utf-8",
   #             headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
   #             response=json.dumps(
   #                 pos_sales_vals, default=str
   #             ),
   #         )
    
    
    @validate_token
    @http.route("/api/pos/sale_details", methods=["POST"], type="http", auth="none", csrf=False)
    def all_project_stages(self, **post):
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        date_from = payload.get("date_from")
        date_to = payload.get("date_to")
        domain = [('date_order', '>=', date_from), ('date_order', '<=', date_to)]
        pos_sale = request.env['pos.order'].search_read(domain)
        if pos_sale:
            pos_sales_vals = [{
                "LOCATION_CODE": 1,
                "TERMINAL_ID": 1,
                "SHIFT_NO": 1,
                'name': pos.get('name'),
                'RCPT_NUM': pos.get('pos_reference'),
                'INV_AMT': pos.get('amount_total'),
                'TAX_AMT': pos.get('amount_tax'),
                'RET_AMT': pos.get('amount_return'),
                'OP_CUR': pos.get('pricelist_id.currency_id.name'),
                'DISCOUNT': pos.get('currency_id.name'),
                'RCPT_DT': pos.get('date_order'),
            } for pos in pos_sale]
            return werkzeug.wrappers.Response(
                status=200,
                content_type="application/json; charset=utf-8",
                headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
                response=json.dumps(
                    pos_sales_vals, default=str
                ),
            )
        else:
            return valid_response([{"message": "No Records to display"}], status=401)

    @validate_token
    @http.route("/api/stage/read", methods=["POST"], type="http", auth="none", csrf=False)
    def read_crm(self, **post):
        user_id = request.uid
        user_obj = request.env['res.users'].browse(user_id)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        project_id = payload.get("project_id")
        stages_obj = request.env['project.task.type']
        # read_stages = stages_obj.with_user(user_obj).filtered(lambda e: int(project_id) in e.project_ids.ids)
        read_stages = stages_obj.with_user(user_obj).search([('project_ids', 'in', [int(project_id)])])
        if read_stages:
            status = 200
            stages_list = []
            for crm in read_stages:
                value_dict = {}
                for f in crm._fields:
                    try:
                        value_dict[f] = str(getattr(crm, f))
                    except AccessError as aee:
                        print(aee)
                stages_list.append(value_dict)
        else:
            stages_list = []
            status = 204
            value_dict = {
                "message": "no data found"
            }
            stages_list.append(value_dict)

        return werkzeug.wrappers.Response(
            status=status,
            content_type="application/json; charset=utf-8",
            headers=[("Cache-Control", "no-store"), ("Pragma", "no-cache")],
            response=json.dumps(
                stages_list
            ),
        )

    @validate_token
    @http.route(["/api/unlinke/project"], methods=["DELETE"], type="http", auth="none", csrf=False)
    def unlink_project(self, **post):
        user_id = request.uid
        user_obj = request.env['res.users'].browse(user_id)
        payload = request.httprequest.data.decode()
        payload = json.loads(payload)
        proj_id = payload.get("project_id")
        proj_obj = request.env['project.project']
        read_projects = proj_obj.with_user(user_obj).search([('id', '=', int(proj_id))])
        if read_projects:
            read_projects.unlink()
            return valid_response(
                [{"message": "Project Id %s successfully deleted" % (proj_id,), "delete": True}])

    # @http.route(["/api/auth/token"], methods=["DELETE"], type="http", auth="none", csrf=False)
    # def delete(self, **post):
    #     """Delete a given token"""
    #     token = request.env["api.access_token"]
    #     access_token = post.get("access_token")
    #
    #     access_token = token.search([("token", "=", access_token)], limit=1)
    #     if not access_token:
    #         error = "Access token is missing in the request header or invalid token was provided"
    #         return invalid_response(400, error)
    #     for token in access_token:
    #         token.unlink()
    #     # Successful response:
    #     return valid_response([{"message": "access token %s successfully deleted" % (access_token,), "delete": True}])
