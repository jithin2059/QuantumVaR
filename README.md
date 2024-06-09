# QuantumVaR

QuantumVaR is a Python application that calculates Value-at-Risk (VaR) using a Quantum Monte Carlo simulation. It utilizes Qiskit, a quantum computing framework, to generate high-quality random numbers for the Monte Carlo simulation, providing potentially more accurate and reliable results compared to classical simulations.
The dashboard includes automated visualizations and VaR required for a particular stock for an investor saying that at 95% confidence level how much money he can lose. 

## Technologies
Python
Qiskit (IBM) quantum computer simulator
Azure VM
Azure CosmosDB for MongoDB
Booststrap
Flask

## Usage

### Prerequisites

Make sure you have the following installed on your machine:

- Python 3.x
- Git

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/jithin2059/QuantumVaR.git
    ```

2. Navigate to the project directory:
    ```bash
    cd QuantumVaR
    ```

3. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To run the application, execute the `app.py` script:

```bash
python3 app.py

### Deployment on Azure Linux VM

Prerequisites
An Azure account with access to the Azure portal.
An existing Linux virtual machine (VM) created on Azure.
Deployment Steps
SSH into your Azure Linux VM:

'''bash
ssh <username>@<public_ip_address>
Replace <username> with your VM username and <public_ip_address> with the public IP address of your VM.
'''

Switch to root user:

'''bash
sudo su
'''

Clone the repository:

'''bash
git clone https://github.com/jithin2059/QuantumVaR.git
'''

Navigate to the project directory:

'''bash
cd QuantumVaR
'''
Install the required Python packages:

'''bash
pip install -r requirements.txt
'''
Run the application:

'''bash
python3 app.py
'''
Access the application:
Open a web browser and navigate to http://<public_ip_address>/ to use the application. Replace <public_ip_address> with the public IP address of your VM.


