"""
短信发送服务
支持阿里云短信和开发模式
"""
import logging
from app.config import settings

logger = logging.getLogger(__name__)

def send_sms_via_aliyun(phone: str, code: str, purpose: str = "login") -> bool:
    """
    通过阿里云短信服务发送验证码
    
    Args:
        phone: 手机号
        code: 验证码
        purpose: 用途（login/register/reset）
    
    Returns:
        bool: 发送是否成功
    """
    try:
        from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
        from alibabacloud_tea_openapi import models as open_api_models
        from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
        from alibabacloud_tea_util import models as util_models
        
        # 配置客户端
        config = open_api_models.Config(
            access_key_id=settings.SMS_ACCESS_KEY_ID,
            access_key_secret=settings.SMS_ACCESS_KEY_SECRET
        )
        config.endpoint = "dysmsapi.aliyuncs.com"
        client = DysmsapiClient(config)
        
        # 根据用途选择模板参数
        template_param = {
            "code": code,
            "purpose": {
                "login": "登录",
                "register": "注册",
                "reset": "重置密码"
            }.get(purpose, "验证")
        }
        
        # 构建请求
        send_request = dysmsapi_models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=settings.SMS_SIGN_NAME,
            template_code=settings.SMS_TEMPLATE_CODE,
            template_param=str(template_param).replace("'", '"')
        )
        
        runtime = util_models.RuntimeOptions()
        
        # 发送短信
        response = client.send_sms_with_options(send_request, runtime)
        
        if response.body.code == "OK":
            logger.info(f"短信发送成功: {phone}")
            return True
        else:
            logger.error(f"短信发送失败: {phone}, 错误: {response.body.message}")
            return False
            
    except ImportError:
        logger.warning("阿里云短信SDK未安装，无法发送真实短信")
        return False
    except Exception as e:
        logger.error(f"发送短信时出错: {str(e)}")
        return False

def send_sms(phone: str, code: str, purpose: str = "login") -> bool:
    """
    发送短信验证码（根据配置选择真实发送或开发模式）
    
    Args:
        phone: 手机号
        code: 验证码
        purpose: 用途
    
    Returns:
        bool: 发送是否成功（开发模式下始终返回True）
    """
    # 开发模式：不发送真实短信
    if settings.SMS_DEV_MODE:
        logger.info(f"[开发模式] 验证码 {code} 应发送到手机 {phone} (用途: {purpose})")
        return True
    
    # 生产模式：发送真实短信
    try:
        return send_sms_via_aliyun(phone, code, purpose)
    except Exception as e:
        logger.error(f"发送短信失败: {str(e)}")
        return False

