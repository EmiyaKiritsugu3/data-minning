/* tables.js — progressive enhancement das tabelas (zero dependências).
 * Para cada table.dataframe / table.data-table: adiciona campo de busca
 * (data-table-filter) e ordenação por clique no cabeçalho.
 * Funciona offline; se o JS não carregar, as tabelas estáticas continuam lá.
 */
(function () {
  function norm(s) {
    return (s || "").toLowerCase();
  }

  function makeSortable(table) {
    var head = table.querySelector("thead tr");
    if (!head) return;
    var ths = Array.prototype.slice.call(head.querySelectorAll("th"));
    var body = table.querySelector("tbody");
    if (!body) return;
    ths.forEach(function (th, idx) {
      th.style.cursor = "pointer";
      th.title = "Clique para ordenar";
      var asc = true;
      th.addEventListener("click", function () {
        var rows = Array.prototype.slice.call(body.querySelectorAll("tr"));
        rows.sort(function (a, b) {
          var av = norm(a.cells[idx] && a.cells[idx].textContent);
          var bv = norm(b.cells[idx] && b.cells[idx].textContent);
          var an = parseFloat(av.replace(",", "."));
          var bn = parseFloat(bv.replace(",", "."));
          var cmp;
          if (!isNaN(an) && !isNaN(bn)) cmp = an - bn;
          else cmp = av < bv ? -1 : av > bv ? 1 : 0;
          return asc ? cmp : -cmp;
        });
        asc = !asc;
        rows.forEach(function (r) {
          body.appendChild(r);
        });
      });
    });
  }

  function addFilter(table) {
    if (table.previousElementSibling &&
        table.previousElementSibling.hasAttribute &&
        table.previousElementSibling.hasAttribute("data-table-filter")) {
      return;
    }
    var input = document.createElement("input");
    input.setAttribute("type", "search");
    input.setAttribute("data-table-filter", "");
    input.placeholder = "Filtrar linhas desta tabela…";
    input.setAttribute("aria-label", "Filtrar linhas da tabela");
    input.className = "table-filter";
    table.parentNode.insertBefore(input, table);
    input.addEventListener("input", function () {
      var q = norm(input.value);
      table.querySelectorAll("tbody tr").forEach(function (tr) {
        tr.style.display = !q || norm(tr.textContent).indexOf(q) !== -1 ? "" : "none";
      });
    });
    makeSortable(table);
  }

  function addGlobalFilter() {
    var g = document.getElementById("global-table-filter");
    if (!g) return;
    g.addEventListener("input", function () {
      var q = norm(g.value);
      document.querySelectorAll("table.dataframe tbody tr, table.data-table tbody tr")
        .forEach(function (tr) {
          tr.style.display = !q || norm(tr.textContent).indexOf(q) !== -1 ? "" : "none";
        });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("table.dataframe, table.data-table").forEach(addFilter);
    addGlobalFilter();
  });
})();
