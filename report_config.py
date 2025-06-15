# report_config.py

COMPANY_NAME = 'MYCOMPANY'
FRONT_IMAGE = 'assets/front_image.jpg'
LOGO_PATH = 'assets/ProtCyber_logo.png'

contents = [
    {"title": "Vulnerability Assessment Report", "page": 2, "indent": 0, "bold": True},
    {"title": "Statement of Confidentiality", "page": 2, "indent": 5},
    {"title": "Scope", "page": 2, "indent": 5},
    {"title": "Executive Summary", "page": 3, "indent": 5},
    {"title": "Recommendations", "page": 4, "indent": 5},
    {"title": "Detailed Analysis", "page": 5, "indent": 5},
    {"title": "Vulnerabilities", "page": 5, "indent": 5},
    {"title": "1. HSTS Missing From HTTPS Server", "page": 5, "indent": 10},
    {"title": "2. SSL Certificate Cannot Be Trusted", "page": 6, "indent": 10},
    {"title": "3. DNS Server BIND version Directive Remote Version Detection", "page": 7, "indent": 10},
    {"title": "4. DNS Server Detection", "page": 7, "indent": 10},
    {"title": "5. SSL/TLS Recommended Cipher Suites", "page": 8, "indent": 10},
    {"title": "Conclusion", "page": 9, "indent": 0, "bold": True},
]

confidentiality_template = [
    "The contents of this document have been developed by Information Security Team at MYCOMPANY for the designated personnel. MYCOMPANY considers the contents of this document to be proprietary and business confidential information. This information is to be used only in the performance of its intended use. This document shall not be distributed to external vendors, partners, or contractors without written authorization from the Responsible Party. Additionally, no portion of this document may be communicated, reproduced, copied or distributed without the prior consent of the Website Owner or Responsible Party."
]

scope_template = [
    "The scope of this security assessment was strictly limited to the webserver identified. ",
    "Our testing efforts were focused exclusively on evaluating the security posture of this single server, encompassing its system configurations, network services, and associated security protocols.",
    "No other systems, networks, or services outside of this specified server were included in this assessment. The aim was to perform a detailed and focused analysis on the website to identify potential vulnerabilities and assess its resilience against security threats."
]

excutive_summary_template = [
    "This security assessment report presents the findings from a comprehensive security scan conducted on the webserver. The server was assessed for various security vulnerabilities across multiple service vectors.",
    "The assessment identified a total of several vulnerabilities that need attention to mitigate potential risks."
]

recommendations_template = [
    "The analysis conducted over the past month provides a clear view of the adversarial tactics and techniques impacting the webserver. It is evident that while some areas show robust defenses, others require strategic enhancements to align with best security practices and the evolving threat landscape. Moving forward, we must integrate the insights from this assessment into our broader security strategy, focusing on areas with frequent alerts and adopting proactive defense measures. This will not only mitigate current vulnerabilities but also prepare us for future security challenges."
]

overviews = [
    {
        'title': "Informative Vulnerabilities",
        'impact': 4,
        'content': [
            {
                'title': 'Impact on Security and Business',
                'text': [
                    "Informative vulnerabilities are typically not direct security flaws but rather provide information about the system that could be valuable to an attacker. Examples include revealing software versions, server banners, or error messages that disclose internal details. While these do not immediately compromise security, they serve as reconnaissance data that attackers can use to plan more targeted attacks.",
                    "From a business perspective, ignoring informative vulnerabilities can lead to indirect risks. For instance, disclosing software versions may allow attackers to identify known exploits associated with those versions, increasing the likelihood of successful attacks. This can eventually result in financial losses, reputational damage, and compliance issues if exploited further."
                ]
            },
            {
                'title': 'How Attackers Exploit Informative Vulnerabilities',
                'text': [
                    "Attackers use these vulnerabilities to gather intelligence about the target environment. For example, an attacker might find out the exact version of a web server or a CMS platform and then search public vulnerability databases for known exploits. This reconnaissance phase is critical because it informs the attacker which vulnerabilities to attempt next, potentially leading to more severe breaches.",
                    "Additionally, information disclosure can expose sensitive data such as usernames, configuration files, or internal IP addresses, which can be leveraged for social engineering or direct attacks on other parts of the network. Thus, while informative vulnerabilities seem harmless, they are often the first step in a multi-stage attack."
                ]
            }
        ]
    },
    {
        'title': "Low Severity Vulnerabilities",
        'impact': 3,
        'content': [
            {
                'title': 'Impact on Security and Business',
                'text': [
                    "Low severity vulnerabilities typically represent minor security weaknesses that by themselves do not allow attackers to cause significant damage but can contribute to a larger attack chain. Examples include missing security headers, minor configuration errors, or verbose error messages that leak some information.",
                    "For businesses, these vulnerabilities may seem negligible but can still erode the overall security posture. Attackers can combine low severity flaws with social engineering or other exploits to escalate their access or cause disruptions. Ignoring these issues can increase the attack surface and potentially lead to costly incidents, including data breaches or service interruptions."
                ]
            },
            {
                'title': 'How Attackers Exploit Informative Vulnerabilities',
                'text': [
                    "Attackers often use low severity vulnerabilities as stepping stones. For instance, a missing security header like X-Frame-Options can enable clickjacking attacks, tricking users into unintended actions that may compromise accounts or data. Similarly, disclosure of usernames or system information can assist attackers in brute-force or credential stuffing attacks.",
                    "A notable example is the PACMAN attack, where a low severity software vulnerability combined with a hardware flaw led to a critical breach. This illustrates that even low severity issues should be addressed proactively to prevent attackers from chaining exploits into more severe attacks."
                ]
            }
        ]
    },
    {
        'title': "Medium Severity Vulnerabilities",
        'impact': 2,
        'content': [
            {
                'title': 'Impact on Security and Business',
                'text': [
                    "Medium severity vulnerabilities arise from misconfigurations or missing security controls that could allow attackers to gain limited unauthorized access or disrupt certain functionalities. Examples include reflected Cross-Site Scripting (XSS), improper session handling, or insufficient access controls.",
                    "For businesses, these vulnerabilities pose a moderate risk. Exploitation can lead to unauthorized data access, session hijacking, or partial system compromise. This can result in financial losses, damage to customer trust, and operational disruptions. Moreover, medium severity flaws can be combined with other vulnerabilities to escalate attacks, increasing their potential impact."
                ]
            },
            {
                'title': 'How Attackers Exploit Informative Vulnerabilities',
                'text': [
                    "Attackers exploit these vulnerabilities to gain footholds within the system. For example, reflected XSS can be used to steal user credentials or perform actions on behalf of users, leading to account takeover or data theft. Improper session management can allow attackers to hijack active sessions, bypassing authentication.",
                    "In some cases, medium severity vulnerabilities serve as pivot points for attackers to explore deeper system weaknesses or launch further attacks, such as privilege escalation or lateral movement within the network. Addressing these vulnerabilities is critical to maintaining robust security."
                ]
            }
        ]
    },
    {
        'title': "High Severity Vulnerabilities",
        'impact': 1,
        'content': [
            {
                'title': 'Impact on Security and Business',
                'text': [
                    "High severity vulnerabilities represent critical security flaws that can be exploited to fully compromise a website or its underlying systems. Examples include SQL injection, remote code execution, authentication bypass, and critical misconfigurations.",
                    "The impact on business can be devastating. Exploitation can lead to complete data breaches, loss of customer data, financial theft, ransomware attacks, and severe reputational damage. Additionally, regulatory fines and legal consequences often follow such incidents. High severity vulnerabilities demand immediate attention and remediation to protect business continuity and trust."
                ]
            },
            {
                'title': 'How Attackers Exploit Informative Vulnerabilities',
                'text': [
                    "Attackers leverage high severity vulnerabilities to gain unauthorized control over systems, extract sensitive data, or disrupt services. For instance, SQL injection allows attackers to manipulate databases, steal or delete data, and even execute arbitrary commands on the server.",
                    "Such vulnerabilities often serve as entry points for widespread attacks, including  ransomware deployment or persistent backdoors. The WannaCry ransomware outbreak is a prime example where an unpatched high severity vulnerability led to a global crisis affecting hundreds of thousands of systems."
                ]
            }
        ]
    }
]

conclusion = [
    "Each vulnerability severity level -from informative to high- plays a distinct role in the security landscape of a website and the wider business ecosystem. Informative and low severity issues primarily provide attackers with valuable reconnaissance or minor footholds, which can be leveraged in multi-stage attacks. Medium severity vulnerabilities allow attackers to gain partial access or disrupt operations, while high severity vulnerabilities can lead to full system compromise with catastrophic business consequences.",
    "Effective vulnerability management requires addressing all severity levels appropriately, understanding their potential impact, and prioritizing remediation efforts to safeguard organizational assets, maintain customer trust, and ensure regulatory compliance."
]
