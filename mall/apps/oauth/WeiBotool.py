# from urllib.parse import parse_qs
# import requests
#
#
# class OAuthWeiBo(object):
#
#     def get_access_token(self,code):
#         access_token_url = "https://api.weibo.com/oauth2/access_token"
#         #组织数据
#         re_dict = requests.post(access_token_url, data={
#             "client_id": 3305669385,
#             "client_secret": "74c7bea69d5fc64f5c3b80c802325276",
#             "grant_type": "authorization_code",
#             "code": code,
#             "redirect_uri": "http://www.meiduo.site:8080/sina_callback.html",
#         })
#         try:
#             # 提取数据
#             datas = re_dict.text
#
#             # data获取到的信息未一个字典'{"access_token":"2.00oneFMeMfeS0889036fBNW_B",
#             # "remind_in":"15799","expires_in":15799,"uid":"5675652",
#             # "isRealName":"true"}'
#
#             # 转化为字典
#             data = eval(datas)
#         except :
#             raise Exception('微博登录错误')
#         # 提取access_token
#         access_token = data.get('access_token', None)
#         print(data)
#         if not access_token :
#             raise Exception('获取失败')
#         print(re_dict)
#         return access_token[0]
#
#     def get_token_info(self,access_token):
#         user_url = 'https://api.weibo.com/oauth2/get_token_info'
#         # user_url = "https://api.weibo.com/2/users/show.json"
#         uid = self.get_access_token().data['uid']
#         get_url = user_url + "?access_token={at}&uid={uid}".format(at=access_token, uid=uid)
#         print(get_url)
#
