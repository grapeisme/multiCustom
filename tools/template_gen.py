#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# -------------------------------------------
#
# @Name: @@@
#
# @Describe: Generate templates of python code
#
#
# @Date:    2013-04-05
#
# @Author:  weigaofeng@baidu.com
#
# -------------------------------------------
# CODE BEGINS
#
#
#
#
#

import sys
from datetime import date

if  __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s newmodule1 newmodule2" % __file__
        sys.exit()

    for module in sys.argv[1:]:
        modulename = module.strip()

        content = """#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# -------------------------------------------
#
# @Name: %(module_)s
#
# @Describe:
#
#
# @Date:    %(date_)s
#
# @Author:  weigaofeng@baidu.com
#
# -------------------------------------------
# CODE BEGINS
#
#
#
#
#
# ----------- DEBUG OR MAIN -----------------
#
if  __name__ == '__main__':
    pass
#
# """ % {'module_': modulename, 'date_': date.today().isoformat()}
        filename = "%s.py" % modulename
        fp = open(filename, 'w')
        fp.write(content)
        fp.close()
    print "%s: %d template(s) generated." % (__file__, len(sys.argv[1:]))



