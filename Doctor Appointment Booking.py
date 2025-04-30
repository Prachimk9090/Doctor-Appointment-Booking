import streamlit as st
import hashlib
import time
import json

# ---------------------- Core Blockchain Classes ----------------------

class Appointment:
    def __init__(self, patient_name, doctor_name, time_slot):
        self.patient_name = patient_name
        self.doctor_name = doctor_name
        self.time_slot = time_slot
        self.timestamp = time.time()

    def to_dict(self):
        return {
            'patient_name': self.patient_name,
            'doctor_name': self.doctor_name,
            'time_slot': self.time_slot,
            'timestamp': self.timestamp
        }


class Block:
    def __init__(self, index, previous_hash, appointment, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.appointment = appointment
        self.timestamp = time.time()
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'appointment': self.appointment.to_dict(),
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty=4):
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []
        self.pending_appointments = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_appointment = Appointment("Genesis", "N/A", "N/A")
        genesis_block = Block(0, "0", genesis_appointment)
        self.chain.append(genesis_block)

    def add_appointment(self, patient_name, doctor_name, time_slot):
        new_appointment = Appointment(patient_name, doctor_name, time_slot)
        self.pending_appointments.append(new_appointment)

    def mine_pending_appointments(self):
        if len(self.pending_appointments) == 0:
            return "No pending appointments to mine."

        last_block = self.chain[-1]
        index = len(self.chain)
        appointment = self.pending_appointments.pop(0)

        new_block = Block(index, last_block.hash, appointment)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

        return f"✅ Appointment booked for {appointment.patient_name} with Dr. {appointment.doctor_name} at {appointment.time_slot}. Block mined: {new_block.hash}"

    def view_chain(self):
        chain_data = []
        for block in self.chain:
            chain_data.append({
                'index': block.index,
                'hash': block.hash,
                'appointment': block.appointment.to_dict(),
                'timestamp': block.timestamp
            })
        return chain_data

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return f"❌ Block {current.index} has been tampered with!"
            if current.previous_hash != prev.hash:
                return f"❌ Block {current.index} has incorrect previous hash!"

        return "✅ Blockchain is valid."

# ---------------------- Streamlit App ----------------------

st.set_page_config(page_title="Blockchain Appointment System", layout="centered")

st.title("🧾 Blockchain Appointment System")

# Initialize blockchain in session_state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()

# Tabs for UI
tab1, tab2, tab3, tab4 = st.tabs(["📅 Book Appointment", "⛏️ Mine Blocks", "🔗 View Blockchain", "✅ Validate Chain"])

# ---------------------- Tab 1: Book Appointment ----------------------
with tab1:
    st.subheader("Book a New Appointment")

    with st.form("appointment_form"):
        patient = st.text_input("Patient Name")
        doctor = st.text_input("Doctor Name")
        time_slot = st.text_input("Time Slot (e.g., 2025-05-01 09:00)")
        submitted = st.form_submit_button("Add Appointment")

        if submitted:
            if patient and doctor and time_slot:
                st.session_state.blockchain.add_appointment(patient, doctor, time_slot)
                st.success("Appointment added to the pending queue.")
            else:
                st.error("Please fill out all fields.")

# ---------------------- Tab 2: Mine Blocks ----------------------
with tab2:
    st.subheader("Mine Pending Appointments")
    if st.button("Mine Next Appointment"):
        result = st.session_state.blockchain.mine_pending_appointments()
        st.info(result)

# ---------------------- Tab 3: View Blockchain ----------------------
with tab3:
    st.subheader("Blockchain Ledger")
    chain_data = st.session_state.blockchain.view_chain()

    for block in chain_data:
        with st.expander(f"Block {block['index']} - Hash: {block['hash'][:10]}..."):
            st.json(block)

# ---------------------- Tab 4: Validate ----------------------
with tab4:
    st.subheader("Validate Blockchain Integrity")

    if st.button("Validate Blockchain"):
        result = st.session_state.blockchain.validate_chain()
        st.info(result)

    if st.button("Tamper with Block 1 (for demo)"):
        try:
            st.session_state.blockchain.chain[1].appointment.patient_name = "Malicious User"
            st.warning("Block 1 has been tampered with.")
        except IndexError:
            st.error("Not enough blocks to tamper with.")
