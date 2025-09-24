# 销售数据分析后端（Python）

该项目提供：
- CSV 销售数据的预处理与统计分析
- 通过 FastAPI 提供 RESTful API

## 技术栈
- FastAPI + Uvicorn（API）
- Pandas / NumPy（数据处理与分析）
- Pydantic v2（数据模型与校验）
- python-multipart（文件上传）
- SQLAlchemy + PyMySQL（MySQL 访问）

## 本地运行（Windows CMD）
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 可选：复制 env 示例并按需修改
copy env.example .env
# 确保本地 MySQL 已创建数据库（如 sales）且账号可访问

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
打开浏览器访问: http://127.0.0.1:8000/docs

## 配置
- 通过 `.env` 或环境变量覆盖默认配置：
  - `DATABASE_URL`，示例：`mysql+pymysql://root:123456@127.0.0.1:3306/sales`
  - `APP_NAME`、`DEBUG`

## 项目结构
```
app/
  api/
    __init__.py
    routes.py
  core/
    __init__.py
    config.py
  db/
    __init__.py
    base.py
    session.py
  schemas/
    __init__.py
    sales.py
  services/
    __init__.py
    preprocess.py
    analyze.py
  utils/
    __init__.py
    csv_io.py
  main.py

data/
  raw/
  processed/

tests/
```

## 下一步开发
- 完成预处理与分析服务核心逻辑
- 定义上传与分析的 API 请求/响应模型
- 增加基础单元测试
- 根据需要新增表模型与持久化逻辑（例如：分析任务记录、上传文件索引等）
```
POST /api/v1/analyze
- 输入：CSV 文件 + 参数（如日期列、金额列、缺失值策略等）
- 输出：清洗结果摘要、基础统计、按维度聚合
```

## 分步实施指南（要做什么 / 如何做 / 预期效果）
1. 搭建与运行本地环境
   - 如何做：创建虚拟环境，安装依赖，复制 `env.example` 为 `.env`，在 MySQL 建库 `sales`。
   - 预期效果：访问 `http://127.0.0.1:8000/docs` 能看到 API 文档。

2. 准备样例 CSV 并验证上传分析
   - 如何做：在 `data/raw/` 放置 `sample.csv`（含列示例：`date,region,product,amount`）。在 docs 中调用 `POST /api/v1/analyze` 上传该文件，并设置 `params`（如 `{"date_column":"date","amount_column":"amount","group_by":["region"],"fill_missing":"median"}`）。
   - 预期效果：返回 `summary`（行列数、金额汇总等）与可选 `groups`（按 region 的总额与条数）。

3. 加强预处理规则（可选）
   - 要做什么：标准化列名、处理空白字符串为缺失、异常值过滤（IQR/3σ）。
   - 如何做：在 `app/services/preprocess.py` 内追加对应逻辑；必要时扩展 `AnalyzeParams`。
   - 预期效果：更稳健的数据清洗，异常输入不影响后续统计。

4. 扩展统计分析能力（可选）
   - 要做什么：按多维度分组；支持多指标聚合（sum/mean/median/max/min）；按日期粒度（D/W/M/Q/Y）统计。
   - 如何做：在 `app/services/analyze.py` 增强 `basic_analysis`，并在 `app/schemas/sales.py` 扩展参数模型。
   - 预期效果：返回更丰富的 `groups` 与指标，满足业务看板所需。

5. 持久化（MySQL）能力（可选，当前未启用）
   - 要做什么：记录上传文件元数据、分析任务日志、结果快照索引等。
   - 如何做：
     - 在 `app/db/base.py` 基础上新增 `app/db/models.py`，定义表结构（SQLAlchemy ORM）。
     - 在 `app/db/session.py` 的 `engine` 上创建表：`from app.db.base import Base; Base.metadata.create_all(bind=engine)`（开发阶段）。
     - 在 API 或服务层写入/读取数据库。
   - 预期效果：可追踪历史任务、复用清洗结果、进一步做任务管理。

6. 新增辅助接口（可选）
   - 要做什么：`GET /api/v1/health` 健康检查；`POST /api/v1/preview` 返回清洗后前 N 行；`GET /api/v1/version` 版本信息。
   - 如何做：在 `app/api/routes.py` 中增加对应路由与返回模型。
   - 预期效果：提高可观测性与调试效率。

7. 测试与样例（推荐）
   - 要做什么：为 `utils/csv_io.py`、`services/preprocess.py`、`services/analyze.py`、`api` 添加基本单元测试。
   - 如何做：在 `tests/` 中新增测试文件；可使用 `pytest`（需要在依赖中加入）。
   - 预期效果：核心流程可回归验证，减少回归风险。

8. 部署与运维（后续）
   - 要做什么：准备生产运行方式与监控（当前阶段可忽略 Docker）。
   - 如何做：配置 `uvicorn` 生产参数、日志、反向代理等。
   - 预期效果：服务稳定对外提供 API。

## 实施路线图（分阶段/层次结构）
- 阶段 0：环境就绪
  - 任务：安装依赖、配置 `.env`、创建 MySQL 数据库
  - 操作：
    - 运行安装命令并启动 `uvicorn`；`copy env.example .env`；在 MySQL 创建 `sales`
  - 交付：可访问 `/docs`；本地能上传 CSV 并返回 `summary`
  - 验收：`POST /api/v1/analyze` 返回 200 且 `summary.rows > 0`

- 阶段 1：预处理增强
  - 任务：列名标准化、空白=缺失、缺失值策略、日期解析稳健性
  - 操作：编辑 `app/services/preprocess.py` 与 `app/schemas/sales.py` 增参；在路由串联参数
  - 交付：带脏数据 CSV 也可稳定输出统计
  - 验收：上传包含空白与异常日期的 CSV，返回不报错且 summary 合理

- 阶段 2：分析能力强化
  - 任务：多维分组与多指标聚合；日期粒度聚合
  - 操作：编辑 `app/services/analyze.py`；更新 `AnalyzeParams` 与响应模型
  - 交付：`groups` 中包含所选指标；支持月度/季度等聚合
  - 验收：指定 `group_by=["region","product"]` 与 `metrics=["sum","mean"]`，结构与数值正确

- 阶段 3：辅助接口
  - 任务：`/health`、`/preview`、`/version`
  - 操作：编辑 `app/api/routes.py`，新增请求/响应模型（如 `PreviewParams`/`PreviewResult`）
  - 交付：预览清洗后前 N 行；健康检查可连通 DB
  - 验收：`/preview` 返回行列；`/health` 在 DB 可用时 200，否则 503

- 阶段 4：持久化（按需）
  - 任务：上传记录与任务记录表；写入分析摘要
  - 操作：`app/db/models.py` 定义 ORM；开发阶段 `create_all`；在 `/analyze` 保存任务
  - 交付：MySQL 有 Upload/AnalysisTask 表并有数据
  - 验收：调用 `/analyze` 后可在表中看到新增记录

- 阶段 5：测试与质量
  - 任务：引入 `pytest`，为 utils/services/api 编写最小测试
  - 操作：在 `requirements.txt` 增加 `pytest`；创建 `tests/*`
  - 交付：`pytest -q` 通过
  - 验收：关键路径（读 CSV、预处理、分析、API）均有至少 1 个测试

- 阶段 6：性能与稳定性（大文件）
  - 任务：分块读取与聚合、返回截断提示、统一错误处理
  - 操作：在 `read_csv_to_dataframe` 支持 `chunksize`；在路由中根据大小采用分块；增加错误拦截
  - 交付：50MB CSV 仍可完成概要统计；大 groups 截断并提示
  - 验收：模拟大 CSV，响应时间与资源可控，返回含 `truncated=true` 字段（建议）

## 实现顺序与可复制提示词（Agent Ready）
- 推荐实现顺序：阶段 0 → 1 → 2 → 3 → 4 → 5 → 6

### 提示词 0：环境就绪
```text
目标：完成环境搭建并运行服务（阶段0）。
改动范围：README、.env、本地环境，无需改代码。
操作：
- 创建 venv、安装依赖、复制 env.example 为 .env，创建 MySQL 数据库 sales。
- 启动 uvicorn app.main:app --reload 并打开 /docs。
验收：/docs 可访问；调用 /api/v1/analyze 返回 200 且 summary.rows>0（用 sample.csv）。
```

### 提示词 1：预处理增强（列名标准化/空白为缺失/缺失策略/日期解析）
```text
目标：增强 app/services/preprocess.py 的预处理逻辑，并在 schemas/路由串联新参数（阶段1）。
改动文件：
- app/services/preprocess.py（实现）
- app/schemas/sales.py（在 AnalyzeParams 中新增：normalize_columns: bool=true、treat_blank_as_na: bool=true、outlier_strategy: str=none|iqr 默认 none）
- app/api/routes.py（把新参数贯通到 preprocess）
要求：
- 列名标准化：去首尾空格，转小写；
- treat_blank_as_na=true 时，将空字符串或仅空白的单元格视为缺失；
- 缺失值策略沿用 fill_missing；
- outlier_strategy=iqr 时，对 amount 列用 IQR 裁剪；
验收：上传包含空白与极端值的 CSV，summary.amount_sum 与没有极端值时更接近；不报错。
```

### 提示词 2：分析能力强化（多指标/多维分组/日期粒度）
```text
目标：增强 app/services/analyze.py 的 basic_analysis（阶段2）。
改动文件：
- app/services/analyze.py（逻辑）
- app/schemas/sales.py（参数：metrics: List[str]，允许 sum|mean|median|max|min|count；响应结构允含多指标）
- app/api/routes.py（接收并传递 metrics、date_granularity、date_column）
要求：
- 支持 group_by 多列；
- 支持 metrics 多指标同时返回（每组 keys 外，增加指标字段）；
- 支持 date_granularity（D/W/M/Q/Y）对 amount 做时间聚合（若提供 date_column）；
验收：group_by=["region","product"], metrics=["sum","mean"], date_granularity="M" 返回结构与数值正确。
```

### 提示词 3：新增预览接口（返回清洗后前 N 行）
```text
目标：新增 POST /api/v1/preview（阶段3）。
改动文件：
- app/schemas/sales.py：新增 PreviewParams(继承/复用 AnalyzeParams) 与 PreviewResult {columns, rows}
- app/api/routes.py：新增 /preview 路由，调用相同预处理，返回前 N 行（默认 20）
要求：
- 复用 read_csv_to_dataframe 与 preprocess；
- 统一编码兼容；
验收：上传 CSV，limit=10，返回列名与 10 行预览。
```

### 提示词 4：健康检查与版本接口
```text
目标：新增 GET /api/v1/health 与 GET /api/v1/version（阶段3）。
改动文件：app/api/routes.py
要求：
- /health：尝试 engine.connect()；成功 200 {status:"ok"}；失败 503 {status:"degraded"}
- /version：返回 {name, version}（取 app/main.py 内 app 信息）
验收：两接口在 docs 可见并可调用。
```

### 提示词 5：MySQL 持久化（上传/任务记录）
```text
目标：引入 ORM 模型并在 /analyze 写入任务记录（阶段4）。
改动文件：
- app/db/models.py：定义 Upload(id, filename, size, created_at)，AnalysisTask(id, upload_id, params_json, result_summary_json, created_at)
- app/db/base.py：确保 Base 汇总；在启动或单独脚本 create_all
- app/api/routes.py：在成功分析后写 AnalysisTask 记录
要求：
- 使用 SessionLocal 管理会话，异常回滚；
- 仅成功分析时写入任务；
验收：调用 /analyze 后，MySQL 中出现新任务记录，包含 params 与 summary。
```

### 提示词 6：基础测试
```text
目标：增加最小测试集（阶段5）。
改动文件：
- requirements.txt：新增 pytest
- tests/test_analyze.py：内存 CSV 调用 /analyze，断言 200 且 summary.rows>0
- tests/test_preprocess.py：构造空白与异常值样本，验证处理逻辑
验收：pytest -q 通过；测试不依赖真实 DB（或做跳过）。
```

### 提示词 7：性能与稳定性（大文件）
```text
目标：支持大 CSV 与稳定返回（阶段6）。
改动文件：
- app/utils/csv_io.py：read_csv_to_dataframe 支持 chunksize；
- app/api/routes.py：根据文件大小选择分块聚合（只统计必要指标）；
- 统一错误处理：返回明确 detail 与建议；
验收：50MB CSV 仍能返回概要统计；groups 超限提示 truncated。
```

## 示例数据
- 现成样例：`data/raw/sample_sales.csv`
- 批量生成：
```bat
D:\sales_venv\Scripts\python scripts\generate_sample_data.py --rows 5000 --out data\raw\generated_sales.csv
```
- 在 `/docs` 中使用 `POST /api/v1/preview` 或 `POST /api/v1/analyze` 上传上述 CSV 进行验证。
