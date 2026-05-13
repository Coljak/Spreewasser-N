export const getOrCreateLegendList = (chart, id) => {
  const legendContainer = document.getElementById(id);
  let listContainer = legendContainer.querySelector('ul');

  if (!listContainer) {
    listContainer = document.createElement('ul');
    listContainer.style.display = 'flex';
    listContainer.style.flexDirection = 'row';
    listContainer.style.margin = 0;
    listContainer.style.padding = 0;

    legendContainer.appendChild(listContainer);
  }

  return listContainer;
};

export const htmlLegendPlugin = {
  id: 'htmlLegend',
  afterUpdate(chart, args, options) {
    const ul = getOrCreateLegendList(chart, options.containerID);

    // Remove old legend items
    while (ul.firstChild) {
      ul.firstChild.remove();
    }

    // Reuse the built-in legendItems generator
    const items = chart.options.plugins.legend.labels.generateLabels(chart);

    items.forEach(item => {
      const li = document.createElement('li');
      li.style.alignItems = 'center';
      li.style.cursor = 'pointer';
      li.style.display = 'flex';
      li.style.flexDirection = 'row';
      li.style.marginLeft = '10px';

      li.onclick = () => {
        const {type} = chart.config;
        if (type === 'pie' || type === 'doughnut') {
          // Pie and doughnut charts only have a single dataset and visibility is per item
          chart.toggleDataVisibility(item.index);
        } else {
          chart.setDatasetVisibility(item.datasetIndex, !chart.isDatasetVisible(item.datasetIndex));
        }
        chart.update();
      };

      // Color box
      const boxSpan = document.createElement('span');
    //   boxSpan.style.background = item.fillStyle;
      boxSpan.style.background = item.strokeStyle;
      boxSpan.style.border = `${item.lineWidth}px solid ${item.strokeStyle}`;
    //   boxSpan.style.borderColor = item.strokeStyle;
    //   boxSpan.style.borderWidth = item.lineWidth + 'px';
      boxSpan.style.display = 'inline-block';
      boxSpan.style.flexShrink = 0;
      boxSpan.style.height = '20px';
      boxSpan.style.marginRight = '10px';
      boxSpan.style.width = '20px';

      // Text
      const textContainer = document.createElement('p');
      textContainer.style.color = item.fontColor;
      textContainer.style.margin = 0;
      textContainer.style.padding = 0;
      textContainer.style.textDecoration = item.hidden ? 'line-through' : '';

      const text = document.createTextNode(item.text);
      textContainer.appendChild(text);

      li.appendChild(boxSpan);
      li.appendChild(textContainer);
      ul.appendChild(li);
    });
  }
};


export const htmlMonicaLegendPlugin = {
  id: 'htmlLegend',

  afterUpdate(chart, args, options) {
    const container = document.getElementById(options.containerID);
    if (!container) return;

    container.innerHTML = '';
    const datasets = chart.data.datasets;

    // -------------------------
    // GROUP DATASETS
    // -------------------------
    const grouped = {};

    datasets.forEach((ds, index) => {
      const sim = ds.simulationIndex ?? 0;

      if (!grouped[sim]) {
        grouped[sim] = {
          label: ds.simulationLabel ?? `Run ${sim}`,
          datasetIndexes: [],
          items: []
        };
      }

      grouped[sim].datasetIndexes.push(index);

      grouped[sim].items.push({
        datasetIndex: index,
        label: ds.label,
        color: ds.borderColor,
        dash: ds.borderDash
      });
    });

    // -------------------------
    // WRAPPER
    // -------------------------
    const wrapper = document.createElement('div');
    wrapper.style.display = 'flex';
    wrapper.style.gap = '16px';
    wrapper.style.flexWrap = 'wrap';

    // -------------------------
    // BUILD GROUP BOXES
    // -------------------------
    Object.entries(grouped).forEach(([simIndex, group]) => {

      const box = document.createElement('div');
      box.style.border = '1px solid #ccc';
      box.style.borderRadius = '8px';
      box.style.padding = '10px';
      box.style.minWidth = '180px';

      // -------------------------
      // GROUP TOGGLE HEADER
      // -------------------------
      const title = document.createElement('div');
      title.textContent = group.label;
      title.style.fontWeight = 'bold';
      title.style.cursor = 'pointer';
      title.style.marginBottom = '8px';

      title.onclick = () => {
        const allVisible = group.datasetIndexes.every(i =>
          chart.isDatasetVisible(i)
        );

        const nextState = !allVisible;

        group.datasetIndexes.forEach(i => {
          chart.setDatasetVisibility(i, nextState);
        });

        chart.update();
      };

      box.appendChild(title);

      // -------------------------
      // LIST
      // -------------------------
      const ul = document.createElement('ul');
      ul.style.listStyle = 'none';
      ul.style.padding = '0';
      ul.style.margin = '0';
      ul.style.display = 'flex';
      ul.style.flexDirection = 'column';
      ul.style.gap = '6px';

      group.items.forEach(item => {

        const li = document.createElement('li');
        li.style.display = 'flex';
        li.style.alignItems = 'center';
        li.style.gap = '8px';
        li.style.cursor = 'pointer';

        li.onclick = () => {
          const visible = chart.isDatasetVisible(item.datasetIndex);
          chart.setDatasetVisibility(item.datasetIndex, !visible);
          chart.update();
        };

        const line = document.createElement('span');
        line.style.width = '22px';
        line.style.borderTop = `3px solid ${item.color}`;
        line.style.display = 'inline-block';

        if (item.dash?.length) {
          line.style.borderTopStyle = 'dashed';
        }

        const text = document.createElement('span');
        text.textContent = item.label;

        const hidden = !chart.isDatasetVisible(item.datasetIndex);
        text.style.textDecoration = hidden ? 'line-through' : 'none';
        text.style.opacity = hidden ? '0.5' : '1';

        li.appendChild(line);
        li.appendChild(text);

        ul.appendChild(li);
      });

      box.appendChild(ul);
      wrapper.appendChild(box);
    });

    container.appendChild(wrapper);
  }
};