你现在直接贴下面这几条命令到终端（每条单独执行，粘贴一行回车一次）：

**第一步 - 切到 FastGPT 目录：**

bash

`cd /Users/mac/fastgpt`

**第二步 - 清残存容器：**

bash

`docker compose down 2>/dev/null; docker stop fastgpt fastgpt-mongo fastgpt-pgvector fastgpt-mongo-init 2>/dev/null; docker rm fastgpt fastgpt-mongo fastgpt-pgvector fastgpt-mongo-init 2>/dev/null; echo "清理完成"`

**第三步 - 下载官方 docker-compose：**

bash

`curl -sL -o docker-compose.yml https://ghproxy.net/https://raw.githubusercontent.com/labring/FastGPT/main/deploy/docker-compose.yml && echo "下载完成"`

**第四步 - 下载 config：**

bash

`curl -sL -o config.json https://ghproxy.net/https://raw.githubusercontent.com/labring/FastGPT/main/deploy/config.json && echo "config完成"`

**第五步 - 查看文件大小验证下载成功：**

bash

`ls -la docker-compose.yml config.json`

**第六步 - 改端口和 OneAPI 配置：**

bash

`sed -i '' 's/"3000:3000"/"3007:3000"/' docker-compose.yml sed -i '' 's|OPENAI_BASE_URL:.*|OPENAI_BASE_URL: http://host.docker.internal:3001/v1|' docker-compose.yml echo "配置完成"`

**第七步 - 建目录启动：**

bash

`mkdir -p mongo/data pgvector/data log && docker compose up -d && sleep 5 && docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"`

每条命令的输出都贴过来，特别是第5步和第7步。如果中间哪条报错就停在那里告诉我。