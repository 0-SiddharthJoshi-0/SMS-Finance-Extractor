# SMS Finance Extractor

A powerful AI-powered system that automatically extracts structured financial information from SMS messages using Google Gemini LLM and a custom-trained BERT model. This project leverages the [crewAI](https://crewai.com) framework to orchestrate multiple AI agents for seamless SMS transaction analysis.

## 🚀 Features

- **SMS Transaction Parsing**: Automatically extracts financial entities from banking SMS messages
- **Multi-Agent Architecture**: Uses specialized AI agents for data reading and entity extraction
- **BERT NER Model**: Custom-trained Named Entity Recognition model for financial SMS analysis
- **Structured Output**: Generates clean JSON with extracted financial data
- **Flexible Input**: Supports both CSV and Excel file formats
- **Google Gemini Integration**: Powered by Google's Gemini 2.5 Flash model

## 📊 Extracted Information

The system extracts the following financial entities from SMS messages:
- **Amount**: Transaction amounts
- **Currency**: Currency codes (AED, USD, etc.)
- **Credit/Debit**: Transaction type (credited/debited)
- **Account Number**: Masked account numbers
- **Balance**: Available account balance
- **Location**: Transaction location/merchant
- **Date**: Transaction date (if available)

## 🛠️ Installation

### Prerequisites
- Python >=3.10 <3.14
- [UV](https://docs.astral.sh/uv/) package manager

### Setup

1. **Install UV** (if not already installed):
```bash
pip install uv
```

2. **Clone the repository**:
```bash
git clone https://github.com/yourusername/sms-finance-extractor.git
cd sms-finance-extractor
```

3. **Install dependencies**:
```bash
uv sync
```

4. **Set up environment variables**:
Create a `.env` file in the root directory:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 📁 Project Structure

```
sms-finance-extractor/
├── knowledge/                 # Data and model files
│   ├── TransactionMemo.csv   # Input SMS data
│   ├── bert-sms-ner-2/       # Trained BERT model
│   └── Annotated_SMS.csv     # Training data
├── src/crewbank/
│   ├── config/               # Agent and task configurations
│   ├── tools/                # Custom tools for data processing
│   └── crew.py              # Main crew orchestration
└── requirements.txt          # Python dependencies
```

## 🚀 Usage

### Basic Usage

Run the SMS extraction pipeline:

```bash
uv run crewai run
```

This will:
1. Read the SMS data from `knowledge/TransactionMemo.csv`
2. Process each SMS message using the BERT NER model
3. Extract financial entities
4. Generate `SMS_NER.json` with structured results

### Advanced Usage

**Training Mode** (for model fine-tuning):
```bash
uv run crewai train <iterations> <filename>
```

**Testing Mode**:
```bash
uv run crewai test <iterations> <eval_llm>
```

**Replay Mode** (replay from specific task):
```bash
uv run crewai replay <task_id>
```

## 📋 Configuration

### Agents Configuration (`src/crewbank/config/agents.yaml`)

The system uses two specialized agents:

1. **CSV Reader Agent**: Reads and prepares transaction data
2. **NER Agent**: Extracts financial entities using the BERT model

### Tasks Configuration (`src/crewbank/config/tasks.yaml`)

Two sequential tasks:
1. **Read CSV Task**: Loads SMS data from CSV files
2. **NER Task**: Performs entity extraction and generates JSON output

## 📊 Output Format

The system generates a JSON file (`SMS_NER.json`) with the following structure:

```json
[
  {
    "ID": "1",
    "Date": "2024-01-15",
    "Amount": "173.00",
    "Currency": "AED",
    "Credit_or_Debit": "credited",
    "AccoutNo": "****0535",
    "Balance": "9054.32",
    "Location": "N/A"
  }
]
```

## 🔧 Customization

### Adding New Entity Types

1. Update the BERT model training data in `knowledge/Annotated_SMS.csv`
2. Retrain the model using the notebook in `knowledge/BERT_SMS.ipynb`
3. Update the `label_map` in `src/crewbank/tools/custom_tool.py`

### Modifying Input Sources

Edit the file path in `src/crewbank/config/tasks.yaml`:
```yaml
read_csv_task:
  args:
    filepath: knowledge/your_new_file.csv
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [crewAI](https://crewai.com) for the multi-agent framework
- [Google Gemini](https://ai.google.dev/) for the LLM capabilities
- [Hugging Face Transformers](https://huggingface.co/transformers/) for the BERT model implementation

## 📞 Support

For support, questions, or feedback:
- Open an issue on GitHub
- Check the [crewAI documentation](https://docs.crewai.com)
- Join the [crewAI Discord](https://discord.com/invite/X4JWnZnxPb)

---

**Built with ❤️ using crewAI and Google Gemini**
