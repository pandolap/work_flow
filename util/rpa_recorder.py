import os
import json
import pickle
import base64
import sys

import traceback
import pandas as pd

from datetime import datetime


CONF_DICT = dict()


def set_home_dir(config_dict):
    if not isinstance(config_dict, dict):
        raise Exception('请用set_home_dir({"home_dir": home_dir})的方式运行')
    current_runtime = datetime.now().strftime("%Y%m%d")
    target_dir = os.path.join(config_dict.get('home_dir'), 'output/{}'.format(current_runtime))
    if target_dir is not None:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        CONF_DICT['ENV_HOME'] = target_dir

        record_target_dir = 'rpa_recorder-' + target_dir
        if record_target_dir not in sys.path:
            sys.path.append(record_target_dir)
    else:
        sys_path_list = sys.path
        try:
            target_dir = next(filter(lambda x: x.startswith('rpa_recorder-'), sys_path_list)).strip('rpa_recorder-')
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            CONF_DICT['ENV_HOME'] = target_dir
        except StopIteration:
            raise Exception('请先在设计器运行set_home_dir({"home_dir": home_dir_path}) 指定流程主目录!')


class BaseLogic:
    _register = dict()

    def __init__(self):
        set_home_dir(dict())
        env_home = CONF_DICT.get('ENV_HOME', '').strip()
        debug = bool(CONF_DICT.get('DEBUG', 'False'))
        if env_home == '':
            raise Exception('请先用 set_home_dir(dir_name) 函数指定主目录!')
        if not os.path.exists(env_home):
            try:
                os.makedirs(env_home)
            except FileNotFoundError:
                raise Exception('主目录创建失败,请检查目录:%s' % env_home)
        self.__dict__['_env_dir'] = env_home
        self.__dict__['_env_title'] = ['变量名', '变量值', '类型']
        self.__dict__['_env_file'] = os.path.join(env_home, 'env.csv')
        self.__dict__['_env_debug'] = debug
        attr_dict = self.get_env()
        for k, v in attr_dict.items():
            self.__dict__[k] = v

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if 'name' in kwargs:
            BaseLogic._register[kwargs['name']] = cls
        else:
            BaseLogic._register[cls.__name__] = cls

    def __setattr__(self, name, value):
        attr_dict = self.get_env()
        attr_dict[name] = value
        self.set_env(attr_dict)
        super().__setattr__(name, value)

    @staticmethod
    def __lazy_load(val):
        if isinstance(val, tuple):
            if len(val) == 3 and val[-1] == '--bl_lazy_load':
                attr_value = val[0]
                attr_type = val[1]
                if attr_type == 'dataframe':
                    if not os.path.exists(attr_value):
                        msg = 'pandas目录文件被人为修改过，请清除env.csv的数据重试！'
                        raise Exception(msg)
                    return pd.read_csv(attr_value)
                elif attr_type == 'object':
                    if not os.path.exists(attr_value):
                        msg = 'pick目录文件被人为修改过，请清除env.csv的数据重试！'
                        raise Exception(msg)
                    with open(attr_value, 'rb') as pf:
                        return pickle.load(pf)
        return val

    def __getattribute__(self, item):
        fn = BaseLogic.__lazy_load
        return fn(object.__getattribute__(self, item))

    def get(self, item, default_value=None):
        if item in self.__dict__:
            return BaseLogic.__lazy_load(self.__dict__[item])
        else:
            return default_value

    def __getitem__(self, item):
        return BaseLogic.__lazy_load(self.__dict__[item])

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __repr__(self):
        item_list = self.items()
        return json.dumps(dict(item_list))

    def __str__(self):
        item_list = self.items()
        return json.dumps(dict(item_list))

    def keys(self):
        key_list = list(filter(lambda x: not x.startswith('_env'), self.__dict__.keys()))
        return key_list

    def items(self):
        key_item_list = list(filter(lambda x: not x[0].startswith('_env'), self.__dict__.items()))
        return key_item_list

    def get_env(self):
        if not os.path.exists(self._env_file):
            with open(self._env_file, 'w', encoding='utf-8') as f:
                f.write(','.join(self._env_title) + '\n')
        attr_dict = dict()
        with open(self._env_file, 'r', encoding='utf-8') as f:
            for n, line in enumerate(f):
                if n == 0:
                    continue
                line = line.strip()
                if len(line) > 0:
                    row = line.split(',')
                    if len(row) < 3:
                        raise Exception('有变量没有按照规则设置')
                    attr_name = row[0]
                    attr_value = row[1]
                    attr_type = row[2]

                    if attr_type == 'str':
                        attr_dict[attr_name] = attr_value
                    elif attr_type == 'int':
                        attr_dict[attr_name] = int(attr_value)
                    elif attr_type == 'float':
                        attr_dict[attr_name] = float(attr_value)
                    elif attr_type in ['list', 'dict']:
                        attr_dict[attr_name] = self.__decode_obj(attr_value)
                    else:
                        attr_dict[attr_name] = (attr_value, attr_type, '--bl_lazy_load')
                    # elif attr_type == 'dataframe':
                    #     attr_dict[attr_name] = pd.read_csv(attr_value)
                    # elif attr_type == 'object':
                    #     if not os.path.exists(attr_value):
                    #         raise Exception('pick目录文件被人为修改过，请清除env.csv的数据重试！')
                    #     with open(attr_value, 'rb') as pf:
                    #         attr_dict[attr_name] = pickle.load(pf)
        return attr_dict

    @staticmethod
    def __encode_obj(obj):
        obj_str = json.dumps(obj)
        obj_bytes = obj_str.encode()
        return str(base64.encodebytes(obj_bytes))

    @staticmethod
    def __decode_obj(obj_str):
        obj_bytes = eval(obj_str)
        return json.loads(base64.decodebytes(obj_bytes))

    def set_env(self, attr_dict):
        if not os.path.exists(self._env_file):
            with open(self._env_file, 'w', encoding='utf-8') as f:
                f.write(','.join(self._env_title) + '\n')

        with open(self._env_file, 'w', encoding='utf-8') as f:
            f.write(','.join(self._env_title) + '\n')
            for k, v in attr_dict.items():
                if isinstance(v, str):
                    f.write(','.join([k, v, 'str']) + '\n')
                elif isinstance(v, int):
                    f.write(','.join([k, str(v), 'int']) + '\n')
                elif isinstance(v, float):
                    f.write(','.join([k, str(v), 'float']) + '\n')
                elif isinstance(v, list):
                    f.write(','.join([k, self.__encode_obj(v), 'list']) + '\n')
                elif isinstance(v, dict):
                    f.write(','.join([k, self.__encode_obj(v), 'dict']) + '\n')
                elif isinstance(v, pd.core.frame.DataFrame):
                    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                    pd_dir = os.path.join(self._log_dir, 'pandas')
                    if not os.path.exists(pd_dir):
                        os.makedirs(pd_dir)
                    pd_file = os.path.join(pd_dir, k + now_str + '.csv')
                    v.to_csv(pd_file, index=False, encoding='utf_8_sig')
                    f.write(','.join([k, pd_file, 'dataframe']) + '\n')
                else:
                    now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                    pick_dir = os.path.join(self._log_dir, 'pickles')
                    if not os.path.exists(pick_dir):
                        os.makedirs(pick_dir)
                    pickle_file = os.path.join(pick_dir, k + now_str + '.pk')
                    with open(pickle_file, 'wb') as pf:
                        pickle.dump(v, pf)
                    f.write(','.join([k, pickle_file, 'object']) + '\n')

    @staticmethod
    def get_register():
        return BaseLogic._register

    @staticmethod
    def run(cmd, *args, **kwargs):
        cmd_cls = BaseLogic._register.get(cmd)
        if cmd_cls is None:
            raise Exception('此命令未被注册！')
        return cmd_cls().fire(*args, **kwargs)

    def fire(self, *args, **kwargs):
        raise Exception('此方法不能直接调用，需要继承该类后重写此方法')

    def clear(self):
        self.backup('flow_end')
        with open(self._env_file, 'w', encoding='utf8') as f:
            f.write(','.join(self._env_title) + '\n')

    def log(self, info):
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = '[{dt}] {info}\n'.format(dt=now_str, info=str(info))
        print(msg)
        with open(self._log_file, 'a', encoding='gb18030') as f:
            f.write(msg)

    @staticmethod
    def backup(step_name, dir_name='default', pre=True):
        env_home = CONF_DICT.get('ENV_HOME', '').strip()
        now = datetime.now()

        year_month_dir = now.strftime('%Y%m')
        day_dir = now.strftime('%d')
        backup_dir = os.path.join(env_home, '日志', year_month_dir, day_dir, dir_name, '变量日志')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        mid_name = ''
        if dir_name == 'default':
            mid_name = now.strftime('%Y%m%d_%H%M%S')

        if pre:
            file_name = step_name + mid_name + '_前.csv'
        else:
            file_name = step_name + mid_name + '_后.csv'

        backup_file = os.path.join(backup_dir, file_name)
        env_file = os.path.join(env_home, 'env.csv')
        if not os.path.exists(env_file):
            return

        with open(backup_file, 'w', encoding='utf-8') as f_out, open(env_file, 'r', encoding='utf-8') as f_in:
            f_out.write(f_in.read())


def rpa_run(name, *args, **kwargs):
    """
    :param name: 该函数注册用的中文名称，如 @register('发票核对'), 则填写'发票核对'
    :return: None
    """
    if name is None or name == '':
        raise Exception('重跑必须指定名称name，如 rerun("发票核对", key="0651-GXAP-20220214-0001")')

    cls = BaseLogic.get_register().get(name)
    if cls is None:
        raise Exception('该函数未被注册，请检查函数名')
    bl = cls()

    try:
        return bl.run(name, *args, **kwargs)
    except:
        bl.log(traceback.format_exc(limit=-1))
        raise


def rpa_rerun(name, key=None, *args, **kwargs):
    """
    :param name: 该函数注册用的中文名称，如 @register('发票核对', key='0651-GXAP-20220214-0001'), 则填写'发票核对'
    :param key: 业务单票的唯一标识，例如单据编号：0651-GXAP-20220214-0001, 选填
    :return: None
    """
    if name is None or name == '':
        raise Exception('重跑必须指定名称name，如 rerun("发票核对", key="0651-GXAP-20220214-0001")')

    cls = BaseLogic.get_register().get(name)
    if cls is None:
        raise Exception('该函数未被注册，请检查函数名')

    env_home = CONF_DICT.get('ENV_HOME', '').strip()
    env_file = os.path.join(env_home, 'env.csv')

    if key is not None:
        dir_name = key
    else:
        dir_name = 'logs'
        print('key名未传入，将在logs目录中查找对应的步骤...')

    def get_default_file(n, bak_dir):
        file_list = sorted(filter(lambda x: x.startswith(n), os.listdir(bak_dir)))
        if len(file_list) > 0:
            return file_list[-1]
        return None

    backup_dir = os.path.join(env_home, '变量变化日志', dir_name)
    if dir_name == 'default':
        step_name = get_default_file(name, backup_dir)
        if step_name is None:
            raise Exception('在default目录未能找到该步骤!')
    else:
        step_name = name + '_前.csv'

    step_file = os.path.join(backup_dir, step_name)
    with open(step_file, 'r', encoding='utf-8') as f_history, open(env_file, 'w', encoding='utf-8') as f_current:
        f_current.write(f_history.read())
    cls().run(name, *args, *kwargs)


def register(name, key=None):
    """
    :param name: 该函数的中文名称，用来表示步骤, 必填
    :param key: 业务单票的唯一标识，例如单据编号：0651-GXAP-20220214-0001, 选填
    :return: None
    """
    if name is None or name == '':
        raise Exception('装饰器必须加上名称，如 @register("发票核对", key="0651-GXAP-20220214-0001")')

    def decorator(func):
        cls_base_name = 'BaseLogic'
        register_dict = BaseLogic.get_register()
        cls_code_num_list = []
        for k, v in register_dict.items():
            cls_item_name = v.__name__
            cls_num = int(cls_item_name.strip(cls_base_name))
            cls_code_num_list.append(cls_num)

        if len(cls_code_num_list) > 0:
            num = max(cls_code_num_list) + 1
            cls_code_name = cls_base_name + str(num)
        else:
            cls_code_name = cls_base_name + str(0)

        cls = type(cls_code_name, (BaseLogic,), {}, name=name)
        cls.fire = func

        env_home = CONF_DICT.get('ENV_HOME', '').strip()
        now = datetime.now()

        current_runtime_dir = now.strftime('%Y%m%d')
        dir_name = key or 'logs'

        log_dir = os.path.join(env_home, 'output', current_runtime_dir, dir_name)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, '{}.log'.format(current_runtime_dir))
        cls._log_dir = log_dir
        cls._log_file = log_file

        def wrapper(*args, **kwargs):

            if key is not None:
                cls.backup(name, dir_name=key, pre=True)
            else:
                cls.backup(name, pre=True)

            cls.run(name, *args, **kwargs)

            if key is not None:
                cls.backup(name, dir_name=key, pre=False)
            else:
                cls.backup(name, pre=False)
        return wrapper
    return decorator
