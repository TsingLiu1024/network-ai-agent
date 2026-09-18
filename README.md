# 🤖 Network AI Agent


<p align="center">

A Multi-Agent AI framework for intelligent network diagnosis,
troubleshooting and automation.

</p>


<p align="center">

Python · FastAPI · RAG · Agent · LLM

</p>


---

# 📖 Introduction


Network AI Agent is an intelligent network troubleshooting system
based on Multi-Agent architecture.


It combines:

- Large Language Models (LLM)
- Retrieval Augmented Generation (RAG)
- Agent Collaboration
- System Diagnostic Tools


The goal is to build an AI-powered SRE assistant that can analyze,
diagnose and provide automated repair suggestions for network problems.



---

# ✨ Features


## 🤖 Multi-Agent Architecture


The system uses multiple specialized agents:


```
                    User
                     |
                     |
              Supervisor Agent
                     |
              Agent Manager
                     |
     --------------------------------
     |              |               |
 Network        Log Agent       RAG Agent
 Agent
     |
     |
 Repair Agent
```


Each Agent focuses on different tasks:


| Agent | Function |
|-|-|
| Network Agent | Network status analysis |
| Log Agent | Windows/Linux log analysis |
| RAG Agent | Knowledge retrieval |
| Repair Agent | Generate repair suggestions |
| Supervisor Agent | Task coordination |



---

# 🧠 RAG Knowledge System


Network AI Agent integrates a Retrieval Augmented Generation pipeline.


Architecture:


```
Knowledge Documents

        |
        |

Document Loader

        |
        |

Text Splitter

        |
        |

Embedding Model

        |
        |

FAISS Vector Database

        |
        |

Retriever

        |
        |

LLM Reasoning

```


Supported knowledge:

- DNS troubleshooting
- Proxy problems
- WSL network issues
- Linux network diagnosis
- OpenWRT troubleshooting



---

# 🔌 LLM Providers


Supported providers:


| Provider | Status |
|-|-|
| Ollama | ✅ |
| DeepSeek API | ✅ |
| OpenAI API | ✅ |


Switch provider:


```env
MODEL_PROVIDER=ollama
```


or


```env
MODEL_PROVIDER=deepseek
```


Example:


```env
MODEL_PROVIDER=deepseek

DEEPSEEK_API_KEY=your_api_key
```



⚠️ Never commit `.env` files containing API keys.



---

# 🛠 Automatic Diagnosis & Repair


The system can generate:


- Network diagnosis report
- Log analysis
- Knowledge-based solutions
- Repair commands


Example:


User:


```
Windows DNS解析失败，无法访问网站
```


System:


```
Analysis:

DNS configuration problem detected


Knowledge:

DNS cache and resolver configuration


Suggestion:

ipconfig /flushdns

netsh winsock reset

```



---

# 🏗 System Architecture


```

                 Client

                   |

                FastAPI

                   |

            Supervisor Agent

                   |

             Agent Manager

                   |

      --------------------------------

      |              |              |

 Network        Log Agent       RAG Agent


                   |

             Repair Agent


                   |

                  LLM


      --------------------------------

      |                            |

   Ollama                      Cloud API

                             
```



---

# 🚀 Installation


## 1. Clone Repository


```bash
git clone https://github.com/TsingLiu1024/network-ai-agent.git

cd network-ai-agent
```



---

## 2. Create Virtual Environment


```bash
python -m venv .venv
```


Activate:


Windows:


```powershell
.venv\Scripts\activate
```



Linux:


```bash
source .venv/bin/activate
```



---

## 3. Install Dependencies


```bash
pip install -r requirements.txt
```



---

# ⚙️ Configuration


Create:


```
.env
```


Example:


```env
# LLM

MODEL_PROVIDER=ollama


# Ollama

OLLAMA_MODEL=deepseek-r1:7b



# DeepSeek

DEEPSEEK_API_KEY=your_key


# RAG

VECTOR_DB_PATH=vector_db

KNOWLEDGE_PATH=knowledge



# Token Optimization

ENABLE_TOKEN_OPTIMIZER=true

```



---

# ▶ Running


Start API:


```bash
python -m uvicorn app:app --reload
```


Default:


```
http://127.0.0.1:8000
```


API Documentation:


```
http://127.0.0.1:8000/docs
```



---

# 📡 API Example


## Request


POST:


```
/diagnose
```


JSON:


```json
{
    "problem":
    "Windows DNS解析失败，无法访问网站"
}
```



## Response Example


```json
{
    "success": true,
    "result": {

        "network": {
            "message":
            "网络检测完成"
        },


        "rag": {
            "message":
            "知识检索完成"
        },


        "repair": {
            "suggestions":[
                {
                    "action":
                    "reset dns",

                    "command":
                    "ipconfig /flushdns"
                }
            ]
        }

    }
}
```



---

# 📂 Project Structure


```
network-ai-agent/

│

├── agents/

│   ├── network_agent.py

│   ├── log_agent.py

│   ├── rag_agent.py

│   ├── repair_agent.py

│   └── core/

│       ├── manager.py

│       ├── supervisor_agent.py

│       └── result.py


├── rag/

│   ├── builder.py

│   ├── retriever.py

│   ├── vectorstore.py

│   └── loader.py


├── llm/

│   ├── ollama.py

│   ├── deepseek.py

│   ├── openai.py

│   └── factory.py


├── knowledge/

│   └── network_docs.txt


├── app.py

├── requirements.txt

└── README.md

```



---

# 🔐 Security


Before uploading to GitHub:


Make sure:


```
.env
```


is ignored.


Example `.gitignore`:


```
.env

__pycache__/

*.pyc

vector_db/

.venv/

```



Never upload:


- API Keys
- Tokens
- Private configuration
- Local vector database



---

# 🗺 Roadmap


## v2.0


Completed:


- [x] Multi-Agent architecture
- [x] Agent Manager
- [x] RAG knowledge retrieval
- [x] FAISS vector database
- [x] Ollama integration
- [x] DeepSeek API integration
- [x] Automatic repair suggestions



---


## v2.1


Planned:


- [ ] Better Supervisor Agent reasoning
- [ ] More network diagnostic tools
- [ ] Tool Calling support
- [ ] Linux network diagnostics



---


## v3.0


Future:


- [ ] Web UI
- [ ] Long-term memory
- [ ] Autonomous repair execution
- [ ] Distributed Agent system



---

# 🤝 Contribution


Contributions are welcome.


Feel free to:

- Submit issues
- Improve agents
- Add knowledge documents
- Add new LLM providers



---

# 📄 License


MIT License


---

# ⭐ Star


If this project helps you,
please consider giving it a ⭐.