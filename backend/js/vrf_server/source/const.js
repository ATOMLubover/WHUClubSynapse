// 在向 redis 中插入时自动增添的前缀
const CODE_PREFIX = 'vrfcode_';

// 错误码
const EnumError =
{
    Success: 0,
    Exception: 1,       // 其他异常

    ErrorRedis: 101,    // redis 错误
    ErrorSend: 102,     // 发送 email 错误
};

module.exports = { CODE_PREFIX, EnumError };