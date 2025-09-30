// "use client"

// import { useEffect, useState } from "react"
// import Link from "next/link"

// export default function Home() {
//   const [mounted, setMounted] = useState(false)

//   useEffect(() => {
//     setMounted(true)
//   }, [])

//   if (!mounted) return null

//   return (
//     <div style={{ backgroundColor: "#ffffff", minHeight: "100vh" }}>
//       <main
//         style={{
//           minHeight: "100vh",
//           display: "flex",
//           flexDirection: "column",
//           alignItems: "center",
//           justifyContent: "center",
//           padding: "20px",
//           maxWidth: "400px",
//           margin: "0 auto",
//         }}
//       >
//         {/* Header */}
//         <header style={{ textAlign: "center", marginBottom: "48px" }} className="fade-in">
//           <div
//             style={{
//               width: "80px",
//               height: "80px",
//               backgroundColor: "#1a73e8",
//               borderRadius: "20px",
//               margin: "0 auto 24px",
//               display: "flex",
//               alignItems: "center",
//               justifyContent: "center",
//               fontSize: "32px",
//             }}
//           >
//             💳
//           </div>
//           <h1
//             style={{
//               fontSize: "28px",
//               fontWeight: "400",
//               marginBottom: "8px",
//               color: "#202124",
//             }}
//           >
//             GlobalPay
//           </h1>
//           <p
//             style={{
//               fontSize: "16px",
//               color: "#5f6368",
//               marginBottom: "16px",
//             }}
//           >
//             Pay from anywhere to anywhere in the world
//           </p>
//           <p
//             style={{
//               fontSize: "14px",
//               color: "#1a73e8",
//               fontWeight: "500",
//             }}
//           >
//             Secure • Fast • Low fees
//           </p>
//         </header>

//         {/* Main Actions */}
//         <section
//           style={{
//             display: "flex",
//             flexDirection: "column",
//             gap: "16px",
//             width: "100%",
//             marginBottom: "32px",
//           }}
//           className="fade-in"
//         >
//           <Link href="/pay" className="pay-button">
//             Send Money (INR → USD)
//           </Link>

//           <Link href="/receive" className="pay-button secondary">
//             Receive Money (USD)
//           </Link>
//         </section>

//         {/* Simple Info */}
//         <div
//           style={{
//             textAlign: "center",
//             padding: "24px",
//             backgroundColor: "#f8f9fa",
//             borderRadius: "12px",
//             width: "100%",
//           }}
//           className="fade-in"
//         >
//           <p
//             style={{
//               fontSize: "14px",
//               color: "#5f6368",
//               lineHeight: "1.4",
//             }}
//           >
//             Lightning fast transactions with very low fees. Secure and reliable global payments.
//           </p>
//         </div>
//       </main>
//     </div>
//   )
// }


import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ethers } from 'ethers';
import { jwtDecode } from 'jwt-decode';
import Web3 from "web3";
import Navigation from './components/Navigation.jsx';
import { LandingPage } from './pages/LandingPage.jsx';
import { Marketplace } from './pages/Marketplace.jsx';
import { ProjectDetail } from './pages/ProjectDetail.jsx';
import { Dashboard } from './pages/Dashboard.jsx';
import { Auth } from './pages/AuthPages/Auth.jsx';
import { AdminDashboard } from './pages/AdminPanel/AdminDashboard.jsx';
import { Certificate } from './pages/Certificate.jsx';
import { RegisterProject } from './pages/RegisterProject.jsx';
import { ProjectOwnerDashboard } from './pages/ProjectOwner/ProjectOwnerDashboard.jsx';

import CarbonMarketPlaceArtifact from './artifacts/contracts/CarbonCycle.sol/CarbonMarketplace.json';

const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('token');

    if (!token) {
        return <Navigate to="/auth" replace />;
    }

    try {
        const decoded = jwtDecode(token);
        const currentTime = Date.now() / 1000;

        if (decoded.exp < currentTime) {
            localStorage.removeItem('token');
            return <Navigate to="/auth" replace />;
        }
    } catch (err) {
        localStorage.removeItem('token');
        return <Navigate to="/auth" replace />;
    }

    return children;
};

function App() {
    const [account, setAccount] = useState('');
    const [contract, setContract] = useState(null);
    const [provider, setProvider] = useState(null);




const setupBlockchain = async () => {
    const contractAddress = "0xaA58F443F0038ba8aB334d78AAeBAAe86D19Ecce";
    const contractABI = [
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "retiredProjectId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "certificateCID",
				"type": "string"
			}
		],
		"name": "CertificateAdded",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "originalProjectId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "newOwnedProjectId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "externalId",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "buyer",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "quantity",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "totalPrice",
				"type": "uint256"
			}
		],
		"name": "ProjectBought",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "projectId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "externalId",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "documentCID",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "quantity",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "ownerName",
				"type": "string"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			}
		],
		"name": "ProjectRegistered",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "originalOwnedProjectId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "newRetiredProjectId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "quantity",
				"type": "uint256"
			}
		],
		"name": "ProjectRetired",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "listedProjects",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "marketplace",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "nextProjectId",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "ownedProjects",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "projects",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "projectId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "externalId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "projectName",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "documentCID",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "retiredProjects",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

    try {
        console.log("🔗 [BLOCKCHAIN] Starting blockchain setup...");
        console.log("🔗 [BLOCKCHAIN] Contract address:", contractAddress);

        if (window.ethereum) {
            // Create web3 instance
            const web3 = new Web3(window.ethereum);
            console.log("🔗 [BLOCKCHAIN] Web3 provider created");

            // Request account access
            await window.ethereum.request({ method: "eth_requestAccounts" });

            const accounts = await web3.eth.getAccounts();
            const selectedAccount = accounts[0];
            console.log("🔗 [BLOCKCHAIN] Account connected:", selectedAccount);

            // Check network
            const networkId = await web3.eth.net.getId();
            console.log("🔗 [BLOCKCHAIN] Connected to network:", { networkId });

            // Contract instance
            const contractInstance = new web3.eth.Contract(contractABI, contractAddress);
            console.log("🔗 [BLOCKCHAIN] Contract instance created");

            // Test: call contract methods
            try {
                const fetchedProjects = await contractInstance.methods.getMarketplace().call();
                console.log("🔗 [BLOCKCHAIN] Fetched projects:", fetchedProjects);

                const nextProjectId = await contractInstance.methods.nextProjectId().call();
                console.log("🔗 [BLOCKCHAIN] Contract test successful - nextProjectId:", nextProjectId);
            } catch (testError) {
                console.error("🔗 [BLOCKCHAIN] Contract test failed:", testError);
            }

            // You can set state here if using React
            setProvider(web3);
            setAccount(selectedAccount);
            setContract(contractInstance);
        } else {
            alert("MetaMask is not installed. Please install it to use this app.");
        }
    } catch (error) {
        console.error("🔗 [BLOCKCHAIN] Error connecting to blockchain:", error);
        console.error("🔗 [BLOCKCHAIN] Error details:", {
            message: error.message,
            stack: error.stack
        });
    }
};


    useEffect(() => {
        const checkConnection = async () => {
            if (window.ethereum) {
                // Check if the user is already connected
                const accounts = await window.ethereum.request({ method: 'eth_accounts' });
                
                // If accounts are found and a token exists, re-establish the connection
                if (accounts.length > 0 && localStorage.getItem('token')) {
                    console.log("User already connected. Re-establishing connection...");
                    setupBlockchain();
                }
            }
        };

        checkConnection();

        // Reload the page if the account changes in MetaMask
        window.ethereum.on('accountsChanged', () => {
            window.location.reload();
        });

    }, []);

    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                <Navigation account={account} setupBlockchain={setupBlockchain}/>
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/auth" element={<Auth setupBlockchain={setupBlockchain} />} />
                    <Route
                        path="/marketplace"
                        element={<Marketplace contract={contract} account={account} />}
                    />
                    <Route
                        path="/dashboard"
                        element={<Dashboard contract={contract} account={account} />}
                    />
                    <Route
                        path="/project/:id"
                        element={<ProjectDetail contract={contract} account={account} />}
                    />
                    <Route
                        path="/certificate/:id"
                        element={<Certificate contract={contract} />}
                    />
                    <Route
                        path="/admin/dashboard"
                        element={
                            <ProtectedRoute>
                                <AdminDashboard />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/owner/register"
                        element={<RegisterProject />}
                    />
                    <Route
                        path="/owner/dashboard"
                        element={<ProjectOwnerDashboard contract={contract} account={account} />}
                    />
                </Routes>
            </div>
        </Router>
    );
}

export default App;