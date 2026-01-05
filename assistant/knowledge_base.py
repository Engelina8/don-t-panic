CONCEPTS = {
    "ransomware": {
        "title": "🔒 Ransomware",
        "definition": "Malware that encrypts files and demands payment for decryption.",
        "what_is_it": "Ransomware is a type of malicious software that prevents access to data by encrypting it until a ransom is paid.",
        "how_it_spreads": [
            "Email attachments (phishing)",
            "Malicious websites and drive-by downloads",
            "Unpatched software vulnerabilities",
            "USB drives and removable media",
            "Remote Desktop Protocol (RDP) exploitation",
            "Supply chain attacks"
        ],
        "signs_of_infection": [
            "Files with new extensions (.locked, .encrypted, .ransomware)",
            "Ransom note displayed on screen or desktop",
            "Unable to access files",
            "System running slowly",
            "Unusual network activity"
        ],
        "how_to_protect": [
            "Regular backups (offline copies)",
            "Email filtering and security",
            "System updates and patches",
            "User security training",
            "Endpoint protection software",
            "Network segmentation",
            "Access control and least privilege"
        ],
        "real_world_examples": [
            "Colonial Pipeline (2021): $4.4M ransom, fuel supply disrupted",
            "JBS Foods (2021): $11M ransom, meat production halted",
            "Hospital Systems (ongoing): Patient care disrupted, lives at risk"
        ],
        "related_scenarios": [
            "Ransomware Attack Response",
            "Advanced Ransomware Incident"
        ]
    },
    "phishing": {
        "title": "🎣 Phishing",
        "definition": "Social engineering attack using deceptive emails/messages to steal credentials or deploy malware.",
        "what_is_it": "Phishing is fraudulent attempt to obtain sensitive information by disguising communications as trustworthy sources.",
        "how_it_works": [
            "Attacker creates fake email (looks legitimate)",
            "Contains malicious link or attachment",
            "User clicks link → malware installed",
            "OR User enters credentials on fake site → credentials stolen",
            "Attacker gains access to systems and data"
        ],
        "red_flags": [
            "Urgent language: 'Act now!', 'Verify account', 'Confirm identity'",
            "Generic greeting: 'Dear Customer' instead of your name",
            "Suspicious sender email address",
            "Requests for password or personal information",
            "Unusual links or attachments",
            "Spelling and grammar errors",
            "Too good to be true offers"
        ],
        "how_to_protect": [
            "Hover over links to check real URL",
            "Never trust sender without verification",
            "Report suspicious emails",
            "Use email filtering",
            "Enable multi-factor authentication",
            "User awareness training",
            "Don't download unexpected attachments"
        ],
        "real_world_examples": [
            "Target (2013): Phishing led to theft of 40M credit cards",
            "Sony (2014): Spear phishing preceded data breach",
            "Business Email Compromise: Billions lost to fake wire transfers"
        ],
        "related_scenarios": [
            "Phishing Email Response",
            "Social Engineering Attack"
        ]
    },
    "ddos": {
        "title": "🌊 DDoS Attacks",
        "definition": "Distributed Denial of Service - overwhelming a system with traffic from multiple sources.",
        "what_is_it": "Attack that floods a target with traffic from many computers, making service unavailable.",
        "types": [
            "Volumetric: Overwhelm bandwidth (UDP floods, DNS amplification)",
            "Protocol: Exploit weaknesses (SYN floods, fragmented packets)",
            "Application: Target apps (HTTP floods, Slowloris)"
        ],
        "signs": [
            "Website/service becomes slow or unresponsive",
            "Legitimate users can't access service",
            "Unusual traffic patterns",
            "Network bandwidth saturated",
            "Server resources exhausted"
        ],
        "mitigation_strategies": [
            "Rate limiting and traffic filtering",
            "DDoS mitigation services (Cloudflare, Akamai)",
            "Network redundancy",
            "Bandwidth over-provisioning",
            "Geo-blocking suspicious traffic",
            "Firewall rules and ACLs",
            "Load balancing"
        ],
        "impact": [
            "Service unavailability",
            "Revenue loss",
            "Reputation damage",
            "Customer frustration",
            "Data loss risk during recovery"
        ],
        "related_scenarios": [
            "DDoS Attack Mitigation",
            "Advanced DDoS Response"
        ]
    },
    "incident_response": {
        "title": "🚨 Incident Response",
        "definition": "Systematic process for handling cybersecurity events and minimizing damage.",
        "four_phases": [
            "1. DETECT & RESPOND: Identify the attack, verify it's real",
            "2. ANALYZE: Understand scope, impact, affected systems",
            "3. CONTAIN: Stop spread, isolate systems, preserve evidence",
            "4. RECOVER: Restore systems, patch, document lessons"
        ],
        "timeline_example": {
            "T+0min": "Alert detected (unusual login attempt)",
            "T+5min": "Verify threat (not false alarm)",
            "T+15min": "Contain: disable account, isolate server",
            "T+1hr": "Analyze: check logs, find entry point",
            "T+4hr": "Recover: restore from backup, change passwords",
            "T+24hr": "Report & learn (post-incident review)"
        },
        "key_skills": [
            "Fast decision-making",
            "Technical knowledge",
            "Communication",
            "Documentation",
            "Calm under pressure"
        ],
        "best_practices": [
            "Have an incident response plan before incident occurs",
            "Document everything",
            "Communicate with stakeholders",
            "Isolate before investigating",
            "Preserve evidence",
            "Work with IT security team"
        ],
        "related_scenarios": [
            "Ransomware Attack Response",
            "Data Breach Investigation",
            "Malware Incident Response"
        ]
    },
    "social_engineering": {
        "title": "🕵️ Social Engineering",
        "definition": "Manipulation of people to divulge confidential information or perform actions.",
        "techniques": [
            "Phishing: Fake emails",
            "Pretexting: Creating false scenario",
            "Baiting: Leaving USB drives with malware",
            "Tailgating: Following someone into restricted area",
            "Quid pro quo: Trading favors for information"
        ],
        "why_it_works": [
            "People are trusting by nature",
            "Attackers exploit psychological principles",
            "Urgency and authority make people comply",
            "Technology is easier to secure than humans"
        ],
        "how_to_defend": [
            "Never share passwords",
            "Verify identities before sharing info",
            "Be suspicious of unsolicited requests",
            "Don't click links from unknown senders",
            "Lock computer when away",
            "Report suspicious behavior",
            "Regular security awareness training"
        ],
        "red_flags": [
            "Unsolicited contact (email, call, person)",
            "Requests for sensitive information",
            "Pressure to act quickly",
            "Too good to be true offers",
            "Generic greetings",
            "Spelling errors in official communications"
        ]
    },
    "network_security": {
        "title": "🔐 Network Security",
        "definition": "Protecting network infrastructure from unauthorized access and attacks.",
        "key_concepts": [
            "Network Segmentation: Divide network into isolated sections",
            "Firewalls: Control incoming/outgoing traffic",
            "VPN: Encrypt remote connections",
            "Intrusion Detection: Monitor for attacks",
            "Access Control: Least privilege principle"
        ],
        "threats": [
            "Man-in-the-Middle (MITM) attacks",
            "Packet sniffing",
            "Network scanning",
            "Unauthorized access",
            "Data interception"
        ],
        "defenses": [
            "Encryption (TLS, IPSec)",
            "Strong authentication",
            "Network monitoring",
            "Regular updates",
            "Secure configuration"
        ]
    },
    "data_breach": {
        "title": "📋 Data Breach",
        "definition": "Unauthorized access to sensitive or confidential data.",
        "what_happens": [
            "Attacker gains unauthorized access",
            "Sensitive data is exfiltrated",
            "Data may be sold or published",
            "Organization and customers affected",
            "Legal and financial consequences"
        ],
        "consequences": [
            "Loss of customer trust",
            "Legal liability and fines",
            "Regulatory compliance issues",
            "Reputation damage",
            "Financial loss",
            "Operational disruption"
        ],
        "response_steps": [
            "Identify what data was accessed",
            "Determine affected individuals",
            "Notify customers and authorities",
            "Implement remediation",
            "Document lessons learned",
            "Improve security"
        ]
    }
}

FAQ = {
    "how_to_start": {
        "question": "How do I start a scenario?",
        "answer": "Go to the Scenarios page and click on any scenario card. Read the scenario brief, then click 'Start' to begin. You'll have unlimited time to complete it."
    },
    "scoring": {
        "question": "How is my score calculated?",
        "answer": """Each scenario has a maximum score (usually 100 points).

Points are awarded for:
• Correct decisions (40%)
• Speed of response (30%)
• Completeness (20%)
• Documentation (10%)

After completing a scenario, you'll see detailed feedback on what went well and what could be improved."""
    },
    "difficulty": {
        "question": "What does each difficulty level mean?",
        "answer": """1 - Beginner: Basic concepts, straightforward decisions
2 - Easy: Simple attack responses, clear guidance
3 - Medium: Balanced challenge, requires knowledge
4 - Hard: Complex scenarios, multiple decisions
5 - Expert: Advanced challenges, high stakes"""
    },
    "time_limit": {
        "question": "Is there a time limit for scenarios?",
        "answer": "No, there's no hard time limit. However, response time affects your score. In real incident response, speed matters - the faster you respond appropriately, the better your score."
    },
    "retry": {
        "question": "Can I retry scenarios?",
        "answer": "Yes! You can retry any scenario unlimited times. Each attempt is recorded separately, so you can see your improvement over time. Your best score counts toward your progress."
    },
    "improvement": {
        "question": "How can I improve my scores?",
        "answer": """1. Learn concepts first using the 'Learn Concepts' section
2. Try easy scenarios first to build confidence
3. Read the detailed feedback after each attempt
4. Focus on your weak areas
5. Take your time to make good decisions
6. Study the best practices provided"""
    },
    "role": {
        "question": "What's my role in these scenarios?",
        "answer": "You are an incident responder or security analyst. Your job is to detect, analyze, contain, and recover from security incidents. You'll make decisions that affect the outcome of the incident."
    },
    "groups": {
        "question": "How do groups work?",
        "answer": "Groups allow instructors to organize trainees. When you join a group, your instructor can track your progress, provide personalized feedback, and see how your performance compares to others in your group."
    }
}

HINTS = {
    "ransomware": {
        "stage_1": "Look for signs of infection. What files have changed? Are there ransom notes on the screen?",
        "stage_2": "You need to understand how bad it is. How many systems are affected? What type of data?",
        "stage_3": "Isolation is critical. Stop the spread by disconnecting affected systems from the network.",
        "stage_4": "Investigation helps you understand the attack. Check logs, find the entry point, and understand the attacker's method.",
        "stage_5": "Recovery means restoring systems safely. Verify backups, restore data, and ensure malware is gone."
    },
    "phishing": {
        "stage_1": "Identify the phishing attack. What are the red flags in this email?",
        "stage_2": "Check the sender and verify authenticity. Does this email really come from who it claims?",
        "stage_3": "Report and contain. Report to security team and mark as phishing.",
        "stage_4": "Educate users. What should people look for to avoid this attack?"
    },
    "ddos": {
        "stage_1": "Detect the attack. What's happening to the system? Is it traffic related?",
        "stage_2": "Analyze the traffic. Where is it coming from? What type of traffic is it?",
        "stage_3": "Implement mitigation. Can you filter, rate limit, or redirect traffic?",
        "stage_4": "Monitor and verify. Is the mitigation working? Is service restored?"
    },
    "data_breach": {
        "stage_1": "Detect unauthorized access. What log entries show abnormal activity?",
        "stage_2": "Identify what data was accessed. Which systems and databases?",
        "stage_3": "Contain the breach. Revoke compromised credentials, change passwords.",
        "stage_4": "Notify stakeholders. Inform affected parties according to regulations."
    }
}

FEEDBACK_RULES = {
    "ransomware": {
        "timing": {
            "excellent": (0, 5),
            "good": (5, 10),
            "okay": (10, 15),
            "slow": (15, 99999)
        },
        "common_mistakes": [
            {
                "key": "restore_immediately",
                "message": "You restored too fast without investigation",
                "tip": "Always investigate BEFORE restoring. Understand the attack method first."
            },
            {
                "key": "skip_backup_check",
                "message": "You didn't verify backup integrity",
                "tip": "Backups may be infected too. Verify they're clean before restoring."
            },
            {
                "key": "notify_too_early",
                "message": "You notified leadership too early (before containment)",
                "tip": "Contain first, then notify. Premature notification can cause panic."
            },
            {
                "key": "skip_logs",
                "message": "You skipped log analysis - missed finding entry point",
                "tip": "Logs tell the story. Always investigate: Who? What? When? How?"
            }
        ],
        "best_practices": [
            "Isolate affected systems immediately",
            "Preserve evidence (logs, memory dumps)",
            "Document every action you take",
            "Notify at the right time (after initial containment)",
            "Investigate before recovery",
            "Verify backups before restoring"
        ]
    },
    "phishing": {
        "timing": {
            "excellent": (0, 2),
            "good": (2, 5),
            "okay": (5, 10),
            "slow": (10, 99999)
        },
        "common_mistakes": [
            {
                "key": "clicked_link",
                "message": "You clicked the suspicious link!",
                "tip": "Always hover over links to check the real URL. Don't trust what you see."
            },
            {
                "key": "entered_password",
                "message": "You entered credentials on fake site",
                "tip": "Official sites NEVER ask for passwords via email. This is always a red flag."
            },
            {
                "key": "opened_attachment",
                "message": "You opened suspicious attachment",
                "tip": "Unexpected attachments are often malware. Scan first or ask sender."
            },
            {
                "key": "skip_verification",
                "message": "You didn't verify the sender",
                "tip": "Always verify sender identity independently. Don't trust email address."
            }
        ],
        "best_practices": [
            "Check sender email carefully",
            "Hover over links to verify URL",
            "Never enter credentials after email request",
            "Report suspicious emails",
            "Educate users about red flags",
            "Use email filtering"
        ]
    },
    "ddos": {
        "timing": {
            "excellent": (0, 3),
            "good": (3, 8),
            "okay": (8, 15),
            "slow": (15, 99999)
        },
        "common_mistakes": [
            {
                "key": "ignored_alert",
                "message": "You ignored early warning signs",
                "tip": "Slow performance can indicate DDoS. Investigate unusual patterns."
            },
            {
                "key": "wrong_mitigation",
                "message": "Your mitigation approach was ineffective",
                "tip": "Different DDoS types need different responses. Analyze traffic first."
            },
            {
                "key": "overloaded_team",
                "message": "You didn't delegate or ask for help",
                "tip": "DDoS response often requires multiple people. Coordinate your team."
            }
        ],
        "best_practices": [
            "Analyze attack type first",
            "Implement appropriate mitigation",
            "Monitor effectiveness",
            "Have mitigation service ready",
            "Communicate with stakeholders",
            "Document attack details"
        ]
    }
}
