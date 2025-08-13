# Proposal

I propose that we really nail down all the communication layers in an agentic driven Cloud product.

From my own reading, I've narrowed things down to one key area of interest. How can we improve upon the Kubernetes reconciler, and what value can be provided byeond what is already offered by k8sgpt?


I understand that there are three primary layers to this.

## Layer 3 The Agentic Swarm
- **Role**: Strategy & Autonomous Action
- **Function**: This top layer is responsible for achieving high-level goals (e.g., "ensure 99.99% uptime," "minimize costs"). It decides what to do. When it detects a problem, it doesn't just know something is wrong; its goal is to fix it. To do that, it needs more information, so it queries the layer below.

I also think that there's further opportunity here. We could have an orchestrator agent within the swarm that's responsible for making strategic decisionsm based on information gathered by child agents from the layer below and data gathered from forecasting models external to the system. 

## Layer 2 K8sGPT, the diagnostic toolkit
- **Role**: Analysis & Explanation
- **Function**: This is the agent's primary tool for understanding _why_ something is wrong. When the agent detects an anomaly (like a failing service), it would invoke K8sGPT.

    An example conversation might look something like:

    **Agent**: My monitoring shows the `payment-service` is unhealthy. What's the root cause?

    **K8sGPT**: I have analyzed the `payment-service` pods. They are in a `CrashLoopBackOff` state. The logs show a fatal error: 'Failed to connect to database: authentication failed.' This is likely caused by an incorrect password in the `db-secret`.


    K8sGPT provides the crucial, context-rich diagnosis that the agent needs to make an intelligent decision.


## Layer 1 Th Reconciler
    - **Role**: Execution & State Enforcement
    - **Function**: After the agent gets the diagnosis from K8sGPT, it formulates a plan and executes it by updating the desired state. 

    The reconciler is idempotent. An example might look something like:

    **Agent**: "The database password is wrong. I will retrieve the correct password from Vault, create a new version of the `db-secret`, and update the deployment to roll our the fix."

    The agent then applies the new configuration to the Kubernetes API. The reconciler sees this new desired state and carries out the orders flawlessly, terminating old pods and starting new ones with the corrected state.
    
    How would Helm fit into this if any? This goes for all the other layers too.



 # Ideas

 1. This was already mentioned before, but having an orchestration agent that makes strategic decisions based on information obtained by the lower layers and information obtained outside the system itself.

 2. We could show a conversation between agents in real time as a way to better demo the thought process and what's occurring at each step within the agentic system. We could use streaming, like the ones people are used to seeing in typical ai chats.