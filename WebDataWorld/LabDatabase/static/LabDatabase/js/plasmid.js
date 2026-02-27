let chart;
            const plasmid_map_div = document.getElementById("plasmid-map-div");
            // '<div class="plasmid-label" style="transform: rotate(0deg) translate(220px) rotate(0deg);">{{backbone.marker}}</div>'
            // '<div class="plasmid-label" style="transform: rotate(90deg) translate(220px) rotate(-90deg);">{{backbone.ori}}</div>'
            ori_list =  document.getElementById("plasmid_marker_info").innerText.split(", ")
            marker_list = document.getElementById("plasmid_ori_info").innerText.split(", ")
            ori_length = ori_list.length
            marker_length = marker_list.length
            total_num = ori_length + marker_length
            each_deg = Math.floor(360 / total_num)
            deg = 0
            console.log(ori_list);
            console.log(marker_list);
            console.log(each_deg);
            ori_list.forEach(item =>{
                const tab = document.createElement("div");
                tab.classList.add("plasmid-label");
                tab.style.transform = `rotate(${deg}deg) translate(220px) rotate(-${deg}deg)`;
                tab.innerText = item;
                deg = deg + each_deg;
                plasmid_map_div.appendChild(tab);
            })
            marker_list.forEach(item =>{
                const tab = document.createElement("div");
                tab.classList.add("plasmid-label");
                tab.style.transform = `rotate(${deg}deg) translate(220px) rotate(-${deg}deg)`;
                tab.innerText = item;
                deg = deg + each_deg;
                plasmid_map_div.appendChild(tab);
            })
            // 质粒图谱交互效果
            document.querySelectorAll('.plasmid-label').forEach(label => {
                label.addEventListener('mouseover', function() {
                    this.style.backgroundColor = 'rgba(255,255,255,0.9)';
                    this.style.boxShadow = '0 0 5px rgba(0,0,0,0.2)';
                    this.style.zIndex = '10';
                });
            
                label.addEventListener('mouseout', function() {
                    this.style.backgroundColor = 'rgba(255,255,255,0.7)';
                    this.style.boxShadow = 'none';
                    this.style.zIndex = '1';
                });
            });

            // parseTreeData();

            initChart();

            document.getElementById('collapseAll').addEventListener('click',collapseAllNodes);

        document.getElementById('downMapButton').addEventListener('click',function(){
            let pathname_list = window.location.pathname.split('/');
            let plasmidid = pathname_list[pathname_list.length -1];
            window.location.href = `/LabDatabase/downloadPlasmidMap/${plasmidid}`;
        })
        // 下载按钮交互
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', function() {
                const originalText = this.innerHTML;
                this.innerHTML = '<i>✓</i> 下载中...';
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    alert('下载完成！');
                }, 1500);
            });
        });

        
        function initChart() {
            const chartDom = document.getElementById('plasmid_tree');
            chart = echarts.init(chartDom);

            updateChart();

            setupEventListeners();

            window.addEventListener('resize',function() {
                chart.resize();
            });
        }

        function getChartOption(treeData){
            const baseOption = {
                title:{
                    text: "层级关系",
                    left: 'center',
                    textStyle :{
                        color:'#2c3e50',
                        fontSize: 20,
                        fontWeight: 'bold'
                    }
                },
                tooltip: {
                    trigger: 'item',
                    triggerOn: 'mousemove',
                    formatter: function(params) {
                        const name = params.name;
                        const value = params.value || 0;
                        const depth = params.data.depth || 0;
                        return `
                        <div style="padding: 5px;">
                            <strong>${name}</strong><br/>
                            深度: ${depth}
                        </div>`;
                    }
                },
                series: [{type: 'tree',
                        data: [treeData],
                        top: '10%',
                        left: '10%',
                        bottom: '10%',
                        right: '30%',
                        symbolSize: 10,
                        label: {
                            position: 'left',
                            verticalAlign: 'middle',
                            align: 'right',
                            fontSize: 14,
                            fontWeight: 'bold',
                            color: '#2c3e50'
                        },
                        leaves: {
                            label: {
                                position: 'right',
                                verticalAlign: 'middle',
                                align: 'left'
                            }
                        },
                        emphasis: {
                            focus: 'descendant',
                            itemStyle: {
                                color: '#2ecc71'
                            }
                        },
                        expandAndCollapse: true,
                        initialTreeDepth: 1,
                        lineStyle: {
                            color: '#95a5a6',
                            width: 2,
                            curveness: 0.2
                        },
                        itemStyle: {
                            color: function(params) {
                                // 根据节点深度设置颜色
                                const depth = params.data.depth;
                                const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6'];
                                return colors[depth % colors.length];
                            },
                            borderColor: '#fff',
                            borderWidth: 2
                        },
                        tooltip: {
                            formatter: function(params) {
                                const name = params.name;
                                const value = params.value || 0;
                                const childrenCount = params.data.children ? params.data.children.length : 0;
                                return `
                                <div style="padding: 10px; min-width: 150px;">
                                    <div style="font-weight: bold; margin-bottom: 5px;">${name}</div>
                                    <div>子节点数: <span style="color: #2ecc71;">${childrenCount}</span></div>
                                    <div>深度: <span style="color: #f39c12;">${params.data.depth}</span></div>
                                </div>`;
                            }
                        }
                    }
                ]
            };
            return baseOption;
        }

        async function parseTreeData(){
            try{
                const plasmidName = document.getElementById("plasmid_name").innerText;

                const response = await fetch(`/LabDatabase/GetParent?PlasmidName=${plasmidName}`);
                const data = await response.json();
                console.log(data);
                    if(data.success) {
                        // console.log(data);
                        let json_value = `{"name":"${plasmidName}","children":[`;
                        // let json_obj = JSON.parse(json_value);
                        let sub_part_value = "";
                        data.parentPart.forEach(part =>{
                            sub_part_value = sub_part_value + `{"name":"${part.name}"},`;
                            // console.log(sub_part_value);
                        })
                        data.parentBackbone.forEach(backbone => {
                            sub_part_value = sub_part_value + `{"name":"${backbone.name}"},`;
                        })
                        // let sub_backbone_obj = JSON.parse(sub_backbone_value);

                        data.parentPlasmid.forEach(part => {
                            sub_part_value = sub_part_value + `{"name":"${plasmid.name}"},`
                        })
                        // let sub_plasmid_obj = JSON.parse(sub_plasmid_value);
                        data.parentInfo.Part.forEach(part => {
                            sub_part_value = sub_part_value + `{"name":"${part}"},`
                        })

                        data.parentInfo.Backbone.forEach(backbone => {
                            sub_part_value = sub_part_value + `{"name":"${backbone}"},`
                        })

                        data.parentInfo.Plasmid.forEach(plasmid => {
                            sub_part_value = sub_part_value + `{"name":${plasmid}},`
                        })


                        sub_part_value = sub_part_value.substring(0,sub_part_value.length-1);
                        json_value = json_value + sub_part_value + "]}";

                        console.log(json_value);
                        // let sub_list = [sub_part_obj, sub_backbone_obj, sub_plasmid_obj];
                        // json_obj.children = sub_list;

                        // let newJsonstr = JSON.stringify(json_obj);
                        // console.log(json_value);
                        console.log(JSON.parse(json_value));
                        return JSON.parse(json_value);
                        // return JSON.parse(json_value);
                    }
                    else{
                        alert('获取数据失败');
                        return null;
                    }
                }
            catch{
                console.log("ssssssssssss");
                alert('数据结构错误');
                return null;
            }
        }

        async function updateChart(){
            console.log("updateChart");
            let treeData = await parseTreeData();
            console.log(treeData);
            if(! treeData) return;

            addDepthInfo(treeData);
            const option = getChartOption(treeData);
            console.log(option);
            chart.setOption(option);
        }

        function addDepthInfo(node, depth = 0){
            node.depth = depth;
            console.log(node);
            if(node.children && node.children.length > 0){
                node.children.forEach(child => {
                    addDepthInfo(child, depth + 1);
                });
            }
        }

        // 展开所有节点
        function expandAllNodes() {
            const option = chart.getOption();
            if (option.series && option.series[0]) {
                option.series[0].initialTreeDepth = 100; // 设置为很大的值
                chart.setOption(option);
            }
        }

        // 折叠所有节点
        function collapseAllNodes() {
            const option = chart.getOption();
            if (option.series && option.series[0]) {
                option.series[0].initialTreeDepth = 0;
                chart.setOption(option);
            }
        }


        // 导出为图片
        function exportToImage() {
            const url = chart.getDataURL({
                type: 'png',
                pixelRatio: 2,
                backgroundColor: '#fff'
            });
            
            const link = document.createElement('a');
            link.download = `树状图_${currentChartType}_${new Date().getTime()}.png`;
            link.href = url;
            link.click();
        }

        async function addNode(plasmidName){
            try{
                const response = await fetch(`/LabDatabase/GetParent?PlasmidName=${plasmidName}`);
                const data = await response.json();
                    if(data.success) {
                        // console.log(data);
                        let json_value = `{"name":"{{plasmid.name}}","children":[`;
                        // let json_obj = JSON.parse(json_value);
                        let sub_part_value = "";
                        data.parentPart.forEach(part =>{
                            sub_part_value = sub_part_value + `{"name":"${part.name}"},`;
                            // console.log(sub_part_value);
                        })
                        data.parentBackbone.forEach(backbone => {
                            sub_part_value = sub_part_value + `{"name":"${backbone.name}"},`;
                        })
                        // let sub_backbone_obj = JSON.parse(sub_backbone_value);

                        data.parentPlasmid.forEach(part => {
                            sub_part_value = sub_part_value + `{"name":"${plasmid.name}"},`
                        })
                        // let sub_plasmid_obj = JSON.parse(sub_plasmid_value);
                        data.parentInfo.Part.forEach(part => {
                            sub_part_value = sub_part_value + `{"name":"${part}"},`
                        })

                        data.parentInfo.Backbone.forEach(backbone => {
                            sub_part_value = sub_part_value + `{"name":"${backbone}"},`
                        })

                        data.parentInfo.Plasmid.forEach(plasmid => {
                            sub_part_value = sub_part_value + `{"name":${plasmid}},`
                        })

                        sub_part_value = sub_part_value.substring(0,sub_part_value.length-1);
                        json_value = json_value + sub_part_value + "]}";
                        // let sub_list = [sub_part_obj, sub_backbone_obj, sub_plasmid_obj];
                        // json_obj.children = sub_list;

                        // let newJsonstr = JSON.stringify(json_obj);
                        // console.log(json_value);
                        // console.log(JSON.parse(json_value));
                        return JSON.parse(json_value);
                        // return JSON.parse(json_value);
                    }
                    else{
                        alert('获取数据失败');
                        return null;
                    }

            }
            catch{
                alert("获取数据失败");
                return null;
            }
        }

        async function setupEventListeners(){
            chart.on('click',function(params){
                if(params.componentType === 'series'&& params.seriesType === 'tree'){
                    const nodeData = params.data;
                    console.log('点击的节点:', nodeData.name);
                    console.log('点击的节点depth：',nodeData.depth);
                    
                }
            })
        }