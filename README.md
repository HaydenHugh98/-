# -
这个软件主要是用于进行数据库表的内容比较（注意是内容比较，不是表结构的比较），校验方面只做了基础的结构一致校验；同步功能是会将备份表truncate，然后copy现有表的全量内容过去；使用前请先用测试表验证逻辑关系，切勿直接使用生产！切勿直接使用生产！切勿直接使用生产！
本人使用是直接将备份的表写死，修改部分在497行到500行内容，可根据需求自己修改
软件目前的修改程度是足够我个人使用，如果有其它需求可以在此基础上修改添加。
代码基本都有注释
软件只是为了解决日常工作中的简单比较，不适用于大型工程
前后根据自己需求改了十来次，这版之后应该短期内不修改了，如果有需要可以在此基础自己diy

This software is mainly used for comparing the contents of database tables (note: it's content comparison, not table structure comparison). The verification aspect only does basic structural consistency checks. The synchronization function will truncate the backup table and then copy all the contents of the current table over. Please verify the logic relationship with a test table before use. Do not use it directly on production! Do not use it directly on production! Do not use it directly on production!

I directly hard-coded the backup table in my use. The modification part is from line 497 to 500. You can modify it according to your needs.

The current modification level of the software is sufficient for my personal use. If you have other needs, you can modify and add on this basis.

Most of the code has comments.

This software is only for solving simple comparisons in daily work and is not suitable for large-scale projects.

I have modified it about ten times according to my needs. I don't think there will be any changes in the short term after this version. If necessary, you can DIY based on this.
---English content source translation software
