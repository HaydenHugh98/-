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


本来想直接上传exe文件供大家直接使用，但是超过25M限制了，软件大概40M，有不想打包的可以直接联系我。

Originally wanted to directly upload exe file for everyone to use directly, but more than 25M limit, software about 40M, do not want to package can contact me directly.



--软件写了有一段时间，有些功能忘记说明：
  1.按住shift左键行表头，可以固定列，固定后的列不能调节宽度，再次释放才可以。
  2.内置是隐藏第一列数据的，因为第一列往往是主键，两侧数据是一致的，可以通过修改配置文件中的hidden_colum_count的值修改
  3.配置文件默认是不带的，首次使用后保存配置文件会在同级文件夹生成一个配置文件，有些内容可以直接在配置文件中修改
  4.本人建议是用视图去进行比较，保证字段格式一致的情况下，还能保证数据安全，软件是配置了备份功能的，视图一定程度可以防止误操作


-- The software has been written for some time, and some functions have forgotten to explain:

1. Hold down the left key of shift to fix the column. The width of the fixed column cannot be adjusted.

2. The built-in data in the first column is hidden, because the first column is usually the primary key, and the data on both sides is consistent. You can change the hidden_colum_count value in the configuration file

3. The configuration file is not brought by default. Saving the configuration file after the first use will generate a configuration file in the same folder, and some contents can be modified directly in the configuration file

4. I suggest using view for comparison to ensure the consistency of field format and data security. The software is configured with backup function, and view can prevent misoperation to a certain extent
