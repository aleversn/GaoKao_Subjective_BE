# SAS Gaokao Benchmark

### API

**Make Config**

```bash
cp config/app_config.json.example api/app_config.json
```

You can set you own `api_key` in `api/app_config.json`, otherwise, the app will run without authentication.

**Start Server**

```bash
cd api/
```

```bash
uvicorn app:app --host=0.0.0.0 --port=8000
```

### Docker

Build and run the docker image

```bash
docker compose up -d --build
```

The code is deploy based on shared storage, so that you can modify the code in the physical machine and the docker container will automatically update the code. So, do not delete any necessary code files in the physical machine.

Restart the docker container

```bash
docker compose restart
```

### License
MIT License

Copyright (c) 2024 Creator SN®

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.