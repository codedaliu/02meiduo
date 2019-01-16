from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client

from mall import settings
from django.utils.deconstruct import deconstructible

@deconstructible
class MyStorage(Storage):

    def __init__(self, config_path=None,config_url=None):
        if not config_path:
            fdfs_config = settings.FDFS_CLIENT_CONF
            self.fdfs_config = fdfs_config
        if not config_url:
            fdfs_url = settings.FDFS_URL
            self.fdfs_url = fdfs_url
    def _open(self,name,mode='rb'):
        pass

    #保存
    def _save(self,name,content,max_length=None):
        # 1.创建Fdfs的客户端
        client = Fdfs_client(self.fdfs_config)
        #２．获取上传的文件
        # name文件名称　
        # content　内容上传的内容　二进制格式
        file_data = content.read()
        #3.上传图片　并获取返回内容
        result = client.upload_by_buffer(file_data)

        if result.get('Status') == 'Upload successed.':
            # 说明上传成功
            file_id = result.get('Remote file_id')
        else:
            raise Exception('上传失败')

            # 需要把file_id 返回回去
        return file_id

    #判断是否存在
    def exists(self, name):
        # Ｆｄｆｓ做了重名的处理
        return False

    def url(self,name):

        # return settings.FDFS_URL + name
        return self.fdfs_url + name