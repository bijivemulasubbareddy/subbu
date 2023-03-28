
const container = document.querySelector(".container");
const nav = document.querySelector(".sidebar");
const main = document.querySelector(".main__content");

container.addEventListener("click", (e) => {
    const toggleBtn = document.querySelector(".nav__toggle--input");
    if (e.target.closest(".sidebar") || e.target.contains(toggleBtn)) {
        return;
    }
    toggleBtn.checked = false;
});

// const myData = {{ shipment_data | tojson }};

console.log(myData);
var appendHtml = "";
myData.map((data, index) => {
    console.log()
    appendHtml = appendHtml + `
      <div id="cardContainer`+ index + `" class="cardContainer mainCard" uuId="` + index + `"
        style=" height:100px;  transition: 0.9s;">
          <div id="firstDisplay">
            <div id="flightDetail">
              <div id="detailLabel"
                style="fontWeight: bold;  color: rgb(252, 178, 50)" > From </div>
                {{delivery_from}}
              <div id="detailLabel">Route_Details</div>
            </div>
            <div id="flightDetail" style="position: relative;top: 15px;">
              <div id="animContainer">
                <div id="anim">
                  <div id="circle" ></div>
                  <div id="circle" ></div>
                  <div id="circle"  ></div>
                </div>
              </div>
              <div id="animContainer" style="left: 62px;">
                <div id="anim">
                  <div id="circle"  ></div>
                  <div id="circle"  ></div>
                  <div id="circle"  ></div>
                </div>
              </div>
              <img style=" width: 30px;margin-left: 33px;"
                src="https://github.com/pizza3/asset/blob/master/airplane2.png?raw=true"/>
            </div>
            <div id="flightDetail" style="position: relative;left: 30px;">
              <div id="detailLabel"
                style="fontWeight: bold;  color: rgb(90, 5, 49)"> To </div>
                {{delivery_to}}
              <div id="detailLabel">Route_Details</div>
            </div>
          </div>
          <div class="first" id="first`+ index + `">
            <div id="firstTop">
              <img style=" height: 51px; margin: 22px 12px; " src="{{src}}"  />
              <div id="timecontainer">
                <div id="detailDate">
                  SCMXPERT
                  lite
                  
                  <div id="detailTime">Shipment_Invoice_Number   :   </div>
                  
                </div>
                <div id="detailDate">
                  <i class="fa-solid fa-ship fa-lg"></i>
                  <div id="detailTime">`+ data.Shipment_Invoice_Number + `</div>
                  June 12
                </div>
              </div>
            </div>
            <div id="firstBehind">
              <div id="firstBehindDisplay">
                <div id="firstBehindRow">
                  <div id="detail">
                    `+ data.Expected_Delivery_Date + `
                    <div id="detailLabel">Expected_Delivery_Date</div>
                  </div>
                  <div id="detail">
                      `+ data.Po_Number + `
                    <div id="detailLabel">Po_Number</div>
                  </div>
                </div>
                <div id="firstBehindRow">
                  <div id="detail">
                    `+ data.Goods_Type + `
                    <div id="detailLabel">Goods_Type</div>
                  </div>
                  <div id="detail">
                    `+ data.Delivery_number + ` <div id="detailLabel">Delivery_number</div>
                  </div>
                </div>
                <div id="firstBehindRow">
                  <div id="detail">
                    `+ data.Device + `
                    <div id="detailLabel">Device</div>
                  </div>
                  <div id="detail">
                     `+ data.NDCNumber + `
                    <div id="detailLabel">NDCNumber</div>
                  </div>
                </div>
                <div class="second" id="second`+ index + `">
                <div id="secondTop" ></div>
                <div id="secondBehind">
                  <div id="secondBehindDisplay">
                    <div id="price">
                      `+ data.Batch_Id + `
                      <div id="priceLabel">Batch_Id</div>
                    </div>
                    <div id="price">
                      `+ data.Serialnumberofgoods + `
                      <div id="priceLabel">Serialnumberofgoods</div>
                    </div>
                    <img
                      id="barCode"
                      src="https://github.com/pizza3/asset/blob/master/barcode.png?raw=true"
                    />
                  </div>
                  <div class = "third" id="third`+ index + `">
                  <div id="thirdTop" ></div>
                  <div id="secondBehindBottom">
                    <button id="button"
                      style=" height: 30px; margin:11px 20px;">
                      Close
                    </button>
                  </div>
                </div>
                </div>
              </div>
              </div>
            </div>
          </div>
        </div>
        `;
})

$("#cardViews").append(appendHtml);

$(document).ready(function () {
    $(".mainCard").click(function () {
        var id = $(this).attr('id');
        var uuid = $(this).attr('uuId');
        var cardStatus = $(this).attr("cardStatus");
        console.log("cardStatus", cardStatus)
        if (cardStatus != "true") {

            $("#cardContainer" + uuid).css('height', '300px');

            $("#first" + uuid).removeClass('firstRemoveAnimation');
            $("#first" + uuid).addClass('firstAddAnimation');

            setTimeout(function () {
                $("#second" + uuid).css('display', 'flex');
                $("#second" + uuid).removeClass('secondRemoveAnimation');
                $("#second" + uuid).addClass('secondAddAnimation');
            }, 700);
            $(this).attr("cardStatus", "true");

            setTimeout(function () {
                $("#third" + uuid).css('display', 'flex');
                $("#third" + uuid).removeClass('thirdRemoveAnimation');
                $("#third" + uuid).addClass('thirdAddAnimation');
            }, 1000);

            $(this).attr("cardStatus", "true");

        } else {


            $("#third" + uuid).css('display', 'flex');
            $("#third" + uuid).addClass('thirdRemoveAnimation');
            $("#third" + uuid).removeClass('thirdAddAnimation');

            setTimeout(function () {
                $("#second" + uuid).removeClass('secondAddAnimation');
                $("#second" + uuid).addClass('secondRemoveAnimation');

            }, 500);


            setTimeout(function () {

                $("#first" + uuid).removeClass('firstAddAnimation');
                $("#first" + uuid).addClass('firstRemoveAnimation');

                $("#cardContainer" + uuid).css('height', '100px');
                $("#cardContainer" + uuid).css('transition', '0.9s');

            }, 750);

            $(this).attr("cardStatus", "false");
        }
    });
});
