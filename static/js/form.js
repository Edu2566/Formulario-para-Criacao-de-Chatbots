document.addEventListener("DOMContentLoaded", () => {
  const steps = Array.from(document.querySelectorAll(".step"));
  const progressBar = document.getElementById("progressBar");
  const prevStepBtn = document.getElementById("prevStep");
  const nextStepBtn = document.getElementById("nextStep");
  const submitBtn = document.getElementById("submitForm");
  const errorBox = document.getElementById("stepError");
  const messageTree = document.getElementById("messageTree");
  const addRootMessageBtn = document.getElementById("addRootMessage");
  const collapseAllBtn = document.getElementById("collapseAll");
  const messagesTreeInput = document.getElementById("messagesTreeInput");
  const form = document.getElementById("chatbotForm");
  const initialTreeData = (() => {
    if (!messageTree) return [];
    const raw = messageTree.dataset.initialTree;
    if (!raw) return [];
    try {
      return JSON.parse(raw);
    } catch (err) {
      console.warn("Não foi possível ler a árvore inicial", err);
      return [];
    }
  })();

  let currentStep = 0;
  let nodeIdCounter = 0;

  const showError = (text) => {
    errorBox.textContent = text;
    errorBox.classList.remove("hidden");
  };

  const clearError = () => {
    errorBox.textContent = "";
    errorBox.classList.add("hidden");
  };

  const updateProgress = () => {
    const percent = ((currentStep + 1) / steps.length) * 100;
    progressBar.style.width = `${percent}%`;
  };

  const toggleNavButtons = () => {
    prevStepBtn.disabled = currentStep === 0;
    const onLastStep = currentStep === steps.length - 1;
    nextStepBtn.classList.toggle("hidden", onLastStep);
    submitBtn.classList.toggle("hidden", !onLastStep);
  };

  const focusFirstInput = () => {
    const target = steps[currentStep].querySelector("input, textarea, button");
    if (target) {
      target.focus({ preventScroll: true });
    }
  };

  const showStep = (index) => {
    currentStep = Math.max(0, Math.min(index, steps.length - 1));
    steps.forEach((step, idx) => {
      step.classList.toggle("hidden", idx !== currentStep);
    });
    toggleNavButtons();
    updateProgress();
    clearError();
    focusFirstInput();
  };

  const computeLabel = (node) => {
    const parts = [];
    let cursor = node;
    while (cursor && cursor !== messageTree) {
      const container = cursor.parentElement;
      const siblings = Array.from(container.querySelectorAll(":scope > .message-node"));
      const position = siblings.indexOf(cursor) + 1;
      parts.unshift(position);
      cursor = container.closest(".message-node");
    }
    return parts.join(".");
  };

  const refreshLabels = () => {
    messageTree.querySelectorAll(".message-node").forEach((node) => {
      const label = node.querySelector("[data-label]");
      if (label) {
        label.textContent = computeLabel(node) || "1";
      }
    });
  };

  const createNodeElement = (value = "", childrenData = []) => {
    const node = document.createElement("div");
    node.className =
      "message-node rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-3 space-y-3 shadow-sm shadow-black/30";
    node.dataset.nodeId = `node-${++nodeIdCounter}`;

    const row = document.createElement("div");
    row.className = "flex items-start gap-3";

    const badge = document.createElement("div");
    badge.dataset.label = "true";
    badge.className =
      "min-w-[2.25rem] h-9 rounded-full bg-aurora/15 border border-aurora/30 text-aurora font-semibold flex items-center justify-center text-sm";

    const input = document.createElement("textarea");
    input.required = true;
    input.rows = 2;
    input.dataset.messageInput = "true";
    input.value = value;
    input.placeholder = "Mensagem (ex.: Digite 1 para fazer X)";
    input.className =
      "flex-1 bg-slate-950/40 border border-slate-800 rounded-xl px-3 py-2 focus:border-aurora focus:ring-2 focus:ring-aurora/30 text-slate-100 placeholder:text-slate-500 resize-y min-h-[60px]";
    input.addEventListener("input", () => {
      input.classList.remove("border-rose-400", "text-rose-100");
    });

    const actions = document.createElement("div");
    actions.className = "flex items-center gap-2";

    const toggleBtn = document.createElement("button");
    toggleBtn.type = "button";
    toggleBtn.dataset.toggleChildren = "true";
    toggleBtn.className =
      "text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 border border-slate-700 hover:border-aurora/40 hover:text-aurora transition";
    toggleBtn.textContent = "Colapsar";

    const addChildBtn = document.createElement("button");
    addChildBtn.type = "button";
    addChildBtn.className =
      "text-xs font-semibold px-3 py-1.5 rounded-lg bg-aurora/15 text-aurora border border-aurora/40 hover:bg-aurora/25 transition";
    addChildBtn.textContent = "+ Subopção";

    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className =
      "text-xs font-semibold px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 border border-slate-700 hover:border-peach/60 hover:text-peach transition";
    removeBtn.textContent = "Remover";

    actions.appendChild(toggleBtn);
    actions.appendChild(addChildBtn);
    actions.appendChild(removeBtn);
    row.appendChild(badge);
    row.appendChild(input);
    row.appendChild(actions);

    const childrenContainer = document.createElement("div");
    childrenContainer.className = "children space-y-3 pl-5 border-l border-slate-800/70";

    addChildBtn.addEventListener("click", () => {
      const child = createNodeElement();
      childrenContainer.appendChild(child);
      refreshLabels();
      child.querySelector("[data-message-input]").focus();
    });

    toggleBtn.addEventListener("click", () => {
      const collapsed = childrenContainer.classList.toggle("hidden");
      toggleBtn.textContent = collapsed ? "Expandir" : "Colapsar";
    });

    removeBtn.addEventListener("click", () => {
      const isRoot = node.parentElement === messageTree;
      const rootCount = messageTree.querySelectorAll(":scope > .message-node").length;
      if (isRoot && rootCount === 1) {
        input.value = "";
        input.focus();
        return;
      }
      node.remove();
      refreshLabels();
    });

    node.appendChild(row);
    node.appendChild(childrenContainer);

    if (childrenData && Array.isArray(childrenData)) {
      childrenData.forEach((child) => {
        const childNode = createNodeElement(child.content || "", child.children || []);
        childrenContainer.appendChild(childNode);
      });
    }

    return node;
  };

  const addRootNode = (value = "", childrenData = []) => {
    const node = createNodeElement(value, childrenData);
    messageTree.appendChild(node);
    refreshLabels();
    node.querySelector("[data-message-input]").focus();
  };

  const ensureAtLeastOneRoot = () => {
    if (!messageTree.querySelector(".message-node")) {
      addRootNode();
    }
  };

  const serializeNodes = (container) => {
    return Array.from(container.querySelectorAll(":scope > .message-node")).map((node) => {
      const input = node.querySelector("[data-message-input]");
      const childrenContainer = node.querySelector(":scope > .children");
      return {
        content: input.value.trim(),
        children: serializeNodes(childrenContainer),
      };
    });
  };

  const validateTree = () => {
    const roots = Array.from(messageTree.querySelectorAll(":scope > .message-node"));
    if (!roots.length) {
      showError("Adicione pelo menos uma mensagem principal.");
      return false;
    }

    let invalidInput = null;
    const walk = (node) => {
      if (invalidInput) return;
      const input = node.querySelector("[data-message-input]");
      if (!input.value.trim()) {
        invalidInput = input;
        return;
      }
      const children = Array.from(node.querySelectorAll(":scope > .children > .message-node"));
      children.forEach(walk);
    };

    roots.forEach(walk);

    if (invalidInput) {
      showError("Preencha todas as mensagens e subopções antes de salvar.");
      invalidInput.classList.add("border-rose-400", "text-rose-100");
      invalidInput.focus();
      return false;
    }

    return true;
  };

  const stepIsValid = (index) => {
    clearError();
    if (index === 0) {
      const nameInput = document.getElementById("name");
      if (!nameInput.value.trim()) {
        showError("Dê um nome ao chatbot para continuar.");
        nameInput.focus();
        return false;
      }
    }

    if (index === 1) {
      return validateTree();
    }

    return true;
  };

  nextStepBtn.addEventListener("click", () => {
    if (!stepIsValid(currentStep)) return;
    showStep(currentStep + 1);
  });

  prevStepBtn.addEventListener("click", () => {
    showStep(currentStep - 1);
  });

  addRootMessageBtn.addEventListener("click", () => {
    addRootNode();
  });

  collapseAllBtn?.addEventListener("click", () => {
    const nodes = messageTree.querySelectorAll(".message-node > .children");
    nodes.forEach((container) => {
      container.classList.add("hidden");
      const toggle = container.parentElement.querySelector('button[data-toggle-children]');
      if (toggle) toggle.textContent = "Expandir";
    });
  });

  form.addEventListener("submit", (event) => {
    const nameValid = stepIsValid(0);
    const treeValid = stepIsValid(1);
    if (!nameValid || !treeValid) {
      event.preventDefault();
      showStep(!nameValid ? 0 : 1);
      return;
    }

    const tree = serializeNodes(messageTree);
    messagesTreeInput.value = JSON.stringify(tree);
  });

  if (initialTreeData.length) {
    initialTreeData.forEach((node) => addRootNode(node.content || "", node.children || []));
    refreshLabels();
  } else {
    ensureAtLeastOneRoot();
  }
  showStep(0);
});
